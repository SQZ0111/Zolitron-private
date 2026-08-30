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

export const MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024

const GERMANY_NAMES = new Set(["germany", "deutschland"])

export function validateUploadInput(files, city, country) {
  if (!files?.length) {
    throw new Error("Please select at least one image.")
  }

  if (!city?.trim()) {
    throw new Error("Please enter a city.")
  }

  if (!GERMANY_NAMES.has(country?.trim().toLowerCase())) {
    throw new Error("Only locations in Germany are supported.")
  }

  const oversizedFile = files.find((file) => file.size > MAX_UPLOAD_SIZE_BYTES)
  if (oversizedFile) {
    throw new Error(`${oversizedFile.name} exceeds the 10 MB upload limit.`)
  }

  const unsupportedFile = files.find((file) => {
    if (file.type) {
      return !["image/jpeg", "image/png"].includes(file.type)
    }
    return !/\.(jpe?g|png)$/i.test(file.name)
  })
  if (unsupportedFile) {
    throw new Error(`${unsupportedFile.name} must be a JPEG or PNG image.`)
  }
}
