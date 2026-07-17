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
}
