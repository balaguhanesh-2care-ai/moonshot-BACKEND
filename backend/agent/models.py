from pydantic import BaseModel, Field


class SearchQueries(BaseModel):
    queries: list[str] = Field(default_factory=list, description="Search queries to find EMR API docs")


class DocSearchResultItem(BaseModel):
    url: str = ""
    title: str = ""
    content: str = ""


class DocSearchResult(BaseModel):
    results: list[DocSearchResultItem] = Field(default_factory=list)


class FetchedDoc(BaseModel):
    url: str = ""
    content: str = ""


class FetchedDocs(BaseModel):
    docs: list[FetchedDoc] = Field(default_factory=list)


class RequestSpec(BaseModel):
    method: str = "POST"
    url: str = ""
    headers: dict[str, str] = Field(default_factory=dict)
    body_template: dict | list | None = None
    fhir_mapping: dict[str, str] = Field(default_factory=dict)
    description: str = ""


class EMRMappingResult(BaseModel):
    push_fhir: list[RequestSpec] = Field(default_factory=list)
    get_fhir: list[RequestSpec] = Field(default_factory=list)


class CritiqueResult(BaseModel):
    confidence: float = Field(ge=0, le=100, description="Confidence score 0-100")
    feedback: str = ""
