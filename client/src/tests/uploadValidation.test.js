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
