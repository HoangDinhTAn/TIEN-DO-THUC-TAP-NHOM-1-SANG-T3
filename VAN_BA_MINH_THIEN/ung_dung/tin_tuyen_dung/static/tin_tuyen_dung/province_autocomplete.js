(() => {
  const list = document.getElementById("vn-provinces");
  if (!list) return;

  const cacheKey = "noi-nghe-vn-provinces-v1";
  const cacheLifetime = 24 * 60 * 60 * 1000;

  function showProvinces(provinces) {
    if (!Array.isArray(provinces)) return;
    const fragment = document.createDocumentFragment();
    provinces.forEach((province) => {
      if (typeof province?.name !== "string" || !province.name.trim()) return;
      const option = document.createElement("option");
      option.value = province.name.trim();
      fragment.appendChild(option);
    });
    list.replaceChildren(fragment);
  }

  try {
    const cached = JSON.parse(sessionStorage.getItem(cacheKey) || "null");
    if (cached && Date.now() - cached.savedAt < cacheLifetime) {
      showProvinces(cached.data);
      return;
    }
  } catch {
    // Ignore unavailable or invalid browser storage and try the API.
  }

  fetch("https://huynhminhvangit.github.io/vn-region-api/data/provinces.json", {
    headers: { Accept: "application/json" },
    signal: AbortSignal.timeout(5000),
  })
    .then((response) => {
      if (!response.ok) throw new Error("Province API unavailable");
      return response.json();
    })
    .then((data) => {
      const provinces = Array.isArray(data) ? data : data?.data;
      if (!Array.isArray(provinces)) throw new Error("Unexpected province API response");
      showProvinces(provinces);
      try {
        sessionStorage.setItem(cacheKey, JSON.stringify({ savedAt: Date.now(), data: provinces }));
      } catch {
        // Suggestions still work for the current page when storage is unavailable.
      }
    })
    .catch(() => {
      // Location fields remain free text when the external API cannot be reached.
    });
})();
