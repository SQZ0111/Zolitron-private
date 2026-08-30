// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Zolitron
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

import { describe, expect, it } from "vitest"

import {
  MAX_UPLOAD_SIZE_BYTES,
  validateUploadInput,
} from "../utils/uploadValidation"

const file = (name = "image.jpg", size = 1024) => ({ name, size })

describe("validateUploadInput", () => {
  it("accepts supported German country names", () => {
    for (const country of ["Germany", "germany", "Deutschland", "deutschland"]) {
      expect(() =>
        validateUploadInput([file()], "Bochum", country),
      ).not.toThrow()
    }
  })

  it("rejects an empty city", () => {
    expect(() => validateUploadInput([file()], " ", "Germany")).toThrow(
      "Please enter a city.",
    )
  })

  it("rejects a country outside Germany", () => {
    expect(() => validateUploadInput([file()], "Bochum", "France")).toThrow(
      "Only locations in Germany are supported.",
    )
  })

  it("rejects files larger than 10 MB", () => {
    expect(() =>
      validateUploadInput(
        [file("large.png", MAX_UPLOAD_SIZE_BYTES + 1)],
        "Bochum",
        "Germany",
      ),
    ).toThrow("large.png exceeds the 10 MB upload limit.")
  })

  it("rejects unsupported file types", () => {
    expect(() =>
      validateUploadInput(
        [{ name: "notes.pdf", size: 1024, type: "application/pdf" }],
        "Bochum",
        "Germany",
      ),
    ).toThrow("notes.pdf must be a JPEG or PNG image.")
  })
})
