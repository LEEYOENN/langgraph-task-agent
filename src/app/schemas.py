from pydantic import BaseModel, Field
from typing import Optional

# 요청 DTO
class AnalysisRequest(BaseModel):
    target_company: str = Field(..., description="투자 분석을 요청할 기업 (ex. 클러쉬)")
    user_query: str = Field(..., description="사용자 질문 (ex. 투자 위험 분석해줘)")

# 응답 DTO
class AnalysisResponse(BaseModel):
    task_id: str
    target_company: str
    status: str
    result_text: Optional[str] = None