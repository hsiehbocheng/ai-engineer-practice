from pydantic import BaseModel, Field

class ParkingInfo(BaseModel):
    """
    將停車資訊轉成結構化輸出，回覆使用者
    如果其中有些資訊不存在，使用 '-' 代替
    """
    parking_name: str = Field(description="停車場名稱")
    parking_type: str = Field(description="停車場類型")
    available_seats: str = Field(description="目前可用車位數")
    parking_fee_description: str = Field(description="收費說明")
    available_time: str = Field(description="營業時間")
    google_maps_url: str = Field(description="到該停車場的 Google Maps 導航連結")

class ParkingInfoList(BaseModel):
    """將各個停車資訊轉為 list 格式提供給使用者，如果沒有的話則為空 list"""
    parking_list: list[ParkingInfo] = Field(default_factory=list, description="停車場資訊列表")

class ToiletInfo(BaseModel):
    pass

class ToiletInfoList(BaseModel):
    toilet_list: list[ToiletInfo] = Field(description="廁所資訊列表")