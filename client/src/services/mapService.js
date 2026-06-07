const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export async function fetchDumpData(city, country) {
  const response = await fetch(`${API_BASE_URL}/api/map/dump-data`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ city, country }),
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch dump data: ${response.status}`);
  }

  return response.json();
}