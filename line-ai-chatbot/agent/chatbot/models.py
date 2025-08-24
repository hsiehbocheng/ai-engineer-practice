from typing import Optional
from pydantic import BaseModel, Field

class ParkingInfo(BaseModel):
    """
    將停車資訊轉成結構化輸出，回覆使用者
    如果其中有些資訊不存在，使用 '-' 代替
    
    Input/Output strictly follow your schemas.
    """
    parking_name: str = Field(description="停車場名稱")
    parking_type: str = Field(description="停車場類型")
    available_seats: str = Field(description="目前可用車位數")
    parking_fee_description: str = Field(description="收費說明")
    available_time: str = Field(description="營業時間")
    google_maps_url: str = Field(description="使用者位置到該停車場的 Google Maps 導航連結")

class ParkingInfoList(BaseModel):
    """將輸入資訊中的各個停車資訊轉為 list 格式提供給使用者，如果沒有的話則為空 list"""
    parking_list: list[ParkingInfo] = Field(default_factory=list, description="停車場資訊列表")

class ToiletInfo(BaseModel):
    """
    將廁所資訊轉成結構化輸出，回覆使用者
    務必與輸入內容一致，不自行添加其他資訊
    除了公廁名稱以外，如果有資訊不存在輸入內容中，使用 '-' 代替
    
    Input/Output strictly follow your schemas.
    """
    toilet_name: str = Field(description="公廁名稱")
    toilet_type: Optional[str] = Field(default=None, description="公廁類型")
    toilet_distance: Optional[str] = Field(default=None, description="與使用者的距離（公尺）")
    toilet_address: Optional[str] = Field(default=None, description="公廁地址")
    toilet_available_seats: Optional[str] = Field(default=None, description="廁所數量")
    toilet_accessible_seats: Optional[str] = Field(default=None, description="無障礙廁所數量")
    toilet_family_seats: Optional[str] = Field(default=None, description="親子廁所數量")
    toilet_google_maps_url: Optional[str] = Field(default=None, description="公廁的 Google Maps 導航連結")

class ToiletInfoList(BaseModel):
    """將輸入資訊中的廁所資訊轉為 list 格式提供給使用者，如果沒有的話則為空 list"""
    toilet_list: list[ToiletInfo] = Field(description="廁所資訊列表")

class AgentStructureResponse(BaseModel):
    """
    將輸入資訊中的停車場或廁所資訊轉為 list 格式提供給使用者，如果沒有的話則為空 list
    務必與輸入內容一致，不自行添加其他資訊
    Input/Output strictly follow your schemas.
    """
    parking_list: list[ParkingInfo] = Field(default_factory=list, description="停車場資訊列表")
    toilet_list: list[ToiletInfo] = Field(default_factory=list, description="廁所資訊列表")