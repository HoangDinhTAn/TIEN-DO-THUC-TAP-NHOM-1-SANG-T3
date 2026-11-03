(() => {
  const $ = (selector, root = document) => root.querySelector(selector);
  const splitList = value => value.split(',').map(item => item.trim()).filter(Boolean);
  const numberOrNull = value => value === '' ? null : Number(value);
  const sessionAuth = () => ({ Authorization: `Bearer ${sessionStorage.getItem('huong.access') || ''}` });
  let currentProfile = null;
  let currentPreferences = null;
  const memoryProfiles = new Map();

  function readDemoProfile(key) {
    if (memoryProfiles.has(key)) return memoryProfiles.get(key);
    try { return JSON.parse(localStorage.getItem(key) || 'null'); } catch { return null; }
  }

  function saveDemoProfile(key, value) {
    memoryProfiles.set(key, value);
    try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* Keep the current demo data in memory for this session. */ }
  }

  function lines(value) {
    return value.split('\n').map(line => line.split('|').map(part => part.trim())).filter(parts => parts.some(Boolean));
  }

  function updateText(selector, value) {
    const node = $(selector);
    if (node) node.textContent = value || 'Chưa cập nhật';
  }

  function renderProfile(profile, preferences) {
    if (!profile) return;
    currentProfile = profile;
    currentPreferences = preferences;
    const user = window.huongApi?.currentUser?.() || {};
    const name = profile.full_name || user.full_name || '';
    updateText('#signed-in-name', name);
    updateText('.account-copy strong', name);
    updateText('#view-profile .profile-hero h2', name);
    updateText('#view-profile .profile-hero>div>p', `${profile.school || 'Chưa cập nhật trường'} · ${profile.major || 'Chưa cập nhật ngành'}`);
    updateText('#view-profile .profile-location', `⌖ ${profile.province || 'Chưa cập nhật địa điểm'}`);
    updateText('#view-profile .profile-main > .profile-section > p', profile.bio || 'Hãy thêm phần giới thiệu để nhà tuyển dụng hiểu hơn về bạn.');

    const chips = $('#view-profile .skill-chips');
    if (chips) {
      chips.replaceChildren();
      (profile.skills || []).forEach(skill => {
        const chip = document.createElement('span');
        chip.textContent = skill.name;
        chips.append(chip);
      });
      const add = document.createElement('span');
      add.textContent = '+ Thêm kỹ năng';
      chips.append(add);
    }

    const project = profile.projects?.[0];
    const projectName = $('#view-profile .project-card strong');
    const projectDescription = $('#view-profile .project-card p');
    if (projectName) projectName.textContent = project?.name || 'Chưa thêm dự án';
    if (projectDescription) projectDescription.textContent = project ? `${project.role || 'Dự án'} · ${(project.technologies || []).join(', ') || project.description || ''}` : 'Thêm dự án thực tế để hồ sơ nổi bật hơn.';

    const preferenceValues = $$('#view-profile .preference-grid strong');
    const roles = preferences?.desired_roles || [];
    const locations = preferences?.locations || [];
    const typeLabels = { internship: 'Thực tập', part_time: 'Bán thời gian', full_time: 'Toàn thời gian', freelance: 'Freelance', remote: 'Remote', hybrid: 'Hybrid' };
    if (preferenceValues[0]) preferenceValues[0].textContent = roles.join(', ') || 'Chưa cập nhật';
    if (preferenceValues[1]) preferenceValues[1].textContent = (preferences?.job_types || []).map(type => typeLabels[type] || type).join(', ') || 'Chưa cập nhật';
    if (preferenceValues[2]) preferenceValues[2].textContent = locations.join(' · ') || 'Chưa cập nhật';
    if (preferenceValues[3]) preferenceValues[3].textContent = preferences?.salary_min != null || preferences?.salary_max != null ? `${preferences.salary_min ?? 0} – ${preferences.salary_max ?? 'thỏa thuận'} / tháng` : 'Thỏa thuận';

    const completeness = profile.completeness ?? 0;
    $$('.profile-strength .panel-heading strong').forEach(node => { node.textContent = `${completeness}%`; });
    $$('.profile-strength .progress-track span').forEach(node => { node.style.width = `${completeness}%`; });
    const visibility = $('#visibility-toggle');
    if (visibility) visibility.checked = profile.visibility === 'public';
  }

  function $$(selector, root = document) { return [...root.querySelectorAll(selector)]; }

  async function loadProfile() {
    if (window.huongApi?.isDemo?.()) {
      const user = window.huongApi.currentUser();
      const cached = readDemoProfile(`huong-profile-${user.id}`);
      if (cached) renderProfile(cached.profile, cached.preferences);
      return;
    }
    try {
      const headers = sessionAuth();
      const [profile, preferences] = await Promise.all([
        window.huongApi.request('/students/me/profile', { headers }),
        window.huongApi.request('/students/me/preferences', { headers }),
      ]);
      renderProfile(profile, preferences);
    } catch (error) {
      window.toast?.(`Không tải được hồ sơ: ${error.message}`);
    }
  }

  async function saveProfile() {
    const fields = Object.fromEntries($$('#modal-content [name]').map(input => [input.name, input.value]));
    const skillItems = splitList(fields.skills).map(name => ({ name, category: 'technical', level: 1, years: 0 }));
    const projectItems = lines(fields.projects).map(([name, role, description, url]) => ({
      name,
      role: role || null,
      description: description || '',
      technologies: [],
      ...(url ? { url } : {}),
    })).filter(item => item.name);
    const experienceItems = lines(fields.experiences).map(([organization, title, description]) => ({
      organization,
      title,
      description: description || '',
      is_current: false,
    })).filter(item => item.organization && item.title);
    const profilePayload = {
      full_name: fields.full_name.trim(),
      phone: fields.phone || null,
      province: fields.province || null,
      bio: fields.bio || null,
      school: fields.school || null,
      faculty: fields.faculty || null,
      major: fields.major || null,
      gpa: numberOrNull(fields.gpa),
      gpa_scale: 4,
      enrollment_year: numberOrNull(fields.enrollment_year),
      graduation_year: numberOrNull(fields.graduation_year),
      skills: skillItems,
      experiences: experienceItems,
      projects: projectItems,
    };
    const preferencePayload = {
      desired_roles: splitList(fields.desired_roles),
      job_types: [fields.job_type],
      locations: splitList(fields.locations),
      salary_min: numberOrNull(fields.salary_min),
      salary_max: numberOrNull(fields.salary_max),
      remote_pref: 'any',
    };
    const button = $('#save-profile');
    button.disabled = true;
    button.textContent = 'Đang lưu…';
    try {
      let profile;
      let preferences;
      if (window.huongApi?.isDemo?.()) {
        const user = window.huongApi.currentUser();
        profile = { ...(currentProfile || {}), ...profilePayload, visibility: fields.visibility, skills: skillItems, experiences: experienceItems, projects: projectItems };
        preferences = { ...(currentPreferences || {}), ...preferencePayload };
        saveDemoProfile(`huong-profile-${user.id}`, { profile, preferences });
      } else {
        const headers = sessionAuth();
        profile = await window.huongApi.request('/students/me/profile', { method: 'PATCH', headers, body: JSON.stringify(profilePayload) });
        preferences = await window.huongApi.request('/students/me/preferences', { method: 'PUT', headers, body: JSON.stringify(preferencePayload) });
        await window.huongApi.request('/students/me/visibility', { method: 'PUT', headers, body: JSON.stringify({ visibility: fields.visibility }) });
        profile.visibility = fields.visibility;
      }
      renderProfile(profile, preferences);
      $('#modal-backdrop').classList.remove('open');
      window.toast?.('Đã lưu hồ sơ và nguyện vọng.');
    } catch (error) {
      window.toast?.(`Chưa lưu được hồ sơ: ${error.message}`);
      button.disabled = false;
      button.textContent = 'Lưu hồ sơ';
    }
  }

  document.addEventListener('click', event => {
    if (event.target.closest('#save-profile') && $('#modal-content [name="full_name"]')) {
      event.preventDefault();
      event.stopImmediatePropagation();
      saveProfile();
    }
  }, true);

  document.addEventListener('click', event => {
    if (event.target.closest('[data-view="profile"]')) loadProfile();
  });

  document.addEventListener('change', async event => {
    if (event.target.id !== 'visibility-toggle') return;
    const visibility = event.target.checked ? 'public' : 'hidden';
    if (window.huongApi?.isDemo?.()) {
      const user = window.huongApi.currentUser();
      const key = `huong-profile-${user.id}`;
      const cached = readDemoProfile(key) || {};
      cached.profile = { ...(cached.profile || currentProfile || {}), visibility };
      saveDemoProfile(key, cached);
      return;
    }
    try {
      await window.huongApi.request('/students/me/visibility', { method: 'PUT', headers: sessionAuth(), body: JSON.stringify({ visibility }) });
      if (currentProfile) currentProfile.visibility = visibility;
    } catch (error) {
      event.target.checked = !event.target.checked;
      window.toast?.(`Không đổi được chế độ hồ sơ: ${error.message}`);
    }
  });

})();
