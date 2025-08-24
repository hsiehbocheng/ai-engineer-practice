import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import asyncio
from math import radians, sin, cos, sqrt, atan2
from typing import Optional

from pydantic import Field, BaseModel
import pandas as pd
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

mcp = FastMCP(name="Toilet")

class ToiletInfo(BaseModel):
    """
    將廁所資訊轉成結構化輸出，回覆使用者
    務必與輸入內容一致，不自行添加其他資訊
    除了公廁名稱以外，如果有資訊不存在輸入內容中，使用 '-' 代替
    """
    toilet_name: str = Field(description="公廁名稱")
    toilet_type: Optional[str] = Field(default=None, description="公廁類型")
    toilet_distance: Optional[float] = Field(default=None, description="與使用者的距離（公尺）")
    toilet_address: Optional[str] = Field(default=None, description="公廁地址")
    toilet_available_seats: Optional[int] = Field(default=None, description="廁所數量")
    toilet_accessible_seats: Optional[int] = Field(default=None, description="無障礙廁所數量")
    toilet_family_seats: Optional[int] = Field(default=None, description="親子廁所數量")

class ToiletInfoList(BaseModel):
    """將輸入資訊中的廁所資訊轉為 list 格式提供給使用者，如果沒有的話則為空 list"""
    toilet_list: list[ToiletInfo] = Field(description="廁所資訊列表")

toilet_df = pd.read_csv(filepath_or_buffer="data/臺北市公廁點位資訊.csv")
toilet_df.rename(columns={
    "行政區": "district",
    "公廁類別": "toilet_type", 
    "公廁名稱": "toilet_name",
    "公廁地址": "toilet_address",
    "經度": "longitude",
    "緯度": "latitude",
    "管理單位": "management_unit",
    "座數": "toilet_available_seats",
    "特優級": "excellent_grade",
    "優等級": "good_grade", 
    "普通級": "normal_grade",
    "改善級": "improvement_grade",
    "無障礙廁座數": "toilet_accessible_seats",
    "親子廁座數": "toilet_family_seats",
    "距離": "toilet_distance"
}, inplace=True)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # 地球半徑 (公里)
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c * 1000  # 回傳公尺

def find_nearby_toilets(lat, lon, distance, top_n=5):
    return_col = list(ToiletInfo.model_json_schema()['properties'].keys())

    toilet_df["toilet_distance"] = toilet_df.apply(
        lambda row: haversine(lat, lon, row["latitude"], row["longitude"]), axis=1
    )
    filtered_df = toilet_df[toilet_df["toilet_distance"] <= distance]
    if not filtered_df.empty:
        return filtered_df.sort_values("toilet_distance").head(top_n)[return_col]
    return toilet_df.sort_values("toilet_distance").head(top_n)[return_col]

@mcp.tool()
async def find_toilet(
    latitude: float = Field(..., description="查詢中心點緯度，例如 25.0375"),
    longitude: float = Field(..., description="查詢中心點經度，例如 121.5637"),
    distance: int = Field(1000, ge=1, le=1000, description="與廁所的距離(公尺)，預設(最大)為 1000"),
) -> ToiletInfoList:
    """
    查詢中心點附近（半徑最多 1000 公尺）的公廁，回傳 JSON 結果。
    Input/Output strictly follow your schemas.
    """
    raw = await asyncio.to_thread(find_nearby_toilets, latitude, longitude, distance)
    raw = raw.to_dict(orient="records")
    
    return ToiletInfoList.model_validate({'toilet_list': raw})

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request):
    return JSONResponse({"status": "200"})

async def main():
    await mcp.run_async(transport="streamable-http", host='0.0.0.0', port=9000)

if __name__ == "__main__":
    asyncio.run(main())