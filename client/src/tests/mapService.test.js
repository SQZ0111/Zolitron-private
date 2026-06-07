import { describe, it, expect, vi, afterEach } from "vitest";
import { fetchDumpData } from "../services/mapService";
import * as mapService from "../services/mapService"



console.log("mapService exports:", mapService);
describe("fetchDumpData", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("sends city and country to the backend and returns dump data", async () => {
    const mockDumpData = [
      {
        id: 1,
        city: "Bochum",
        country: "Germany",
        latitude: 51.4818,
        longitude: 7.2162,
        type: "fly_dump",
        confidence: 0.92,
        description: "Detected possible illegal dumping site.",
      },
    ];

    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: vi.fn().mockResolvedValue(mockDumpData),
    });

    vi.stubGlobal("fetch", fetchMock);

    const result = await fetchDumpData("Bochum", "Germany");

    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/api/map/dump-data",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          city: "Bochum",
          country: "Germany",
        }),
      },
    );

    expect(result).toEqual(mockDumpData);
  });

  it("throws an error if the backend response is not ok", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
    });

    vi.stubGlobal("fetch", fetchMock);

    await expect(fetchDumpData("Bochum", "Germany")).rejects.toThrow(
      "Failed to fetch dump data: 500",
    );
  });
});