# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Zolitron
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.api import ClassificationRead


class CameraFrameBatchImportRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    size: int = Field(default=5, ge=1, le=25)
    cursor: str | None = Field(default=None)
    created_from: str | None = Field(default=None, alias="createdFrom")
    created_to: str | None = Field(default=None, alias="createdTo")


class CameraFrameBatchJobStartResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    job_id: str = Field(serialization_alias="jobId")


class CameraFrameBatchJobStatusResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    job_id: str = Field(serialization_alias="jobId")
    state: str
    progress: int
    message: str
    items: list[ClassificationRead] = Field(default_factory=list)
    cursor: str | None = Field(default=None)
    new_count: int = Field(default=0, serialization_alias="newCount")
    duplicate_count: int = Field(default=0, serialization_alias="duplicateCount")
    error: str | None = None
