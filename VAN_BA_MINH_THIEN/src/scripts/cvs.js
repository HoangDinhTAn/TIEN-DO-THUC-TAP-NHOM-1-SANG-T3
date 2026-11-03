(() => {
  const maxBytes = 10 * 1024 * 1024;
  let cvs = [];
  let demoMemory = [];
  const $ = (selector, root = document) => root.querySelector(selector);

  function getUser() { return window.huongApi?.currentUser?.() || {}; }
  function demoKey() { return `huong-cvs-${getUser().id || 'guest'}`; }
  function feedback(message, isError = false) {
    const node = $('#cv-feedback');
    if (!node) return;
    node.textContent = message;
    node.classList.toggle('error', isError);
  }

  function installCVSection() {
    if ($('#cv-list')) return;
    const profileMain = $('#view-profile .profile-main');
    const preferenceSection = profileMain && [...profileMain.querySelectorAll(':scope > .profile-section')].find(section => section.textContent.includes('Nguyện vọng nghề nghiệp'));
    if (!profileMain || !preferenceSection) return;
    const section = document.createElement('div');
    section.className = 'profile-section cv-section';
    section.innerHTML = '<div class="section-title"><div><h3>CV của tôi</h3><p>Tải PDF/DOCX tối đa 10 MB. Hãy kiểm tra kỹ thông tin sau khi trích xuất.</p></div><label class="button button-outline cv-upload-label" for="cv-file-input">＋ Tải CV lên</label><input id="cv-file-input" type="file" accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document" hidden></div><div id="cv-list" class="cv-list"><div class="cv-empty">Chưa có CV nào được tải lên.</div></div><div id="cv-feedback" class="cv-feedback" role="status" aria-live="polite"></div>';
    profileMain.insertBefore(section, preferenceSection);
  }

  async function loadCVs() {
    installCVSection();
    if (!$('#cv-list')) return;
    if (window.huongApi?.isDemo?.()) {
      try { demoMemory = JSON.parse(localStorage.getItem(demoKey()) || '[]'); } catch { /* File-open demo keeps its list in memory. */ }
      cvs = demoMemory;
      renderCVs();
      return;
    }
    try {
      cvs = await window.huongApi.request('/students/me/cvs', { headers: { Authorization: `Bearer ${sessionStorage.getItem('huong.access') || ''}` } });
      renderCVs();
    } catch (error) {
      feedback(`Không tải được danh sách CV: ${error.message}`, true);
    }
  }

  function saveDemoCVs() {
    try { localStorage.setItem(demoKey(), JSON.stringify(demoMemory)); } catch { /* Keep demo list in memory only. */ }
    cvs = demoMemory;
    renderCVs();
  }

  function renderCVs() {
    const list = $('#cv-list');
    if (!list) return;
    list.replaceChildren();
    if (!cvs.length) {
      const empty = document.createElement('div');
      empty.className = 'cv-empty';
      empty.textContent = 'Chưa có CV nào được tải lên.';
      list.append(empty);
      return;
    }
    cvs.forEach(cv => {
      const card = document.createElement('article');
      card.className = 'cv-card';
      const icon = document.createElement('span');
      icon.className = 'cv-file-icon';
      icon.textContent = cv.media_type === 'application/pdf' ? 'PDF' : 'DOCX';
      const main = document.createElement('div');
      main.className = 'cv-card-main';
      const titleRow = document.createElement('div');
      titleRow.className = 'cv-title-row';
      const name = document.createElement('strong');
      name.textContent = cv.original_name;
      titleRow.append(name);
      if (cv.is_default) {
        const badge = document.createElement('span');
        badge.className = 'cv-default-badge';
        badge.textContent = 'CV mặc định';
        titleRow.append(badge);
      }
      const meta = document.createElement('small');
      meta.textContent = `${(cv.size_bytes / (1024 * 1024)).toFixed(2)} MB · ${cv.parse_status === 'complete' ? 'Đã trích xuất' : cv.parse_status === 'failed' ? 'Trích xuất lỗi' : 'Chưa phân tích'}`;
      main.append(titleRow, meta);
      const actions = document.createElement('div');
      actions.className = 'cv-actions';
      if (!cv.is_default) actions.append(actionButton('Đặt mặc định', 'cv-default', cv.id));
      if (cv.parse_status !== 'complete') actions.append(actionButton('Phân tích', 'cv-parse', cv.id));
      actions.append(actionButton('Xóa', 'cv-delete', cv.id, true));
      card.append(icon, main, actions);
      list.append(card);
      if (cv.parsed_json) list.append(renderParsed(cv.parsed_json));
      if (cv.parse_error) {
        const error = document.createElement('p');
        error.className = 'cv-parse-error';
        error.textContent = cv.parse_error;
        list.append(error);
      }
    });
  }

  function actionButton(label, action, id, danger = false) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = `cv-action${danger ? ' danger' : ''}`;
    button.textContent = label;
    button.dataset[action] = id;
    return button;
  }

  function renderParsed(parsed) {
    const box = document.createElement('div');
    box.className = 'cv-parsed-box';
    const heading = document.createElement('strong');
    heading.textContent = 'Thông tin trích xuất — hãy rà soát trước khi cập nhật hồ sơ';
    box.append(heading);
    const list = document.createElement('ul');
    const fields = [
      ['Email', parsed.email],
      ['Điện thoại', parsed.phone],
      ['Kỹ năng nhận diện', (parsed.skills || []).join(', ') || null],
    ];
    fields.forEach(([label, value]) => {
      const item = document.createElement('li');
      item.textContent = `${label}: ${value || 'Không tìm thấy'}`;
      list.append(item);
    });
    box.append(list);
    const note = document.createElement('small');
    note.textContent = 'Bản trích xuất hiện dùng nhận diện văn bản và từ khóa cơ bản; thông tin chưa tự ghi vào hồ sơ.';
    box.append(note);
    return box;
  }

  async function upload(file) {
    if (!file) return;
    const ext = file.name.split('.').pop().toLowerCase();
    if (!['pdf', 'docx'].includes(ext)) return feedback('Chỉ hỗ trợ PDF hoặc DOCX.', true);
    if (file.size > maxBytes) return feedback('CV phải có kích thước tối đa 10 MB.', true);
    feedback('Đang tải CV lên…');
    try {
      if (window.huongApi?.isDemo?.()) {
        const demoCV = { id: `demo-cv-${Date.now()}`, original_name: file.name, media_type: ext === 'pdf' ? 'application/pdf' : 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', size_bytes: file.size, is_default: demoMemory.length === 0, parse_status: 'not_parsed' };
        demoMemory = [demoCV, ...demoMemory.map(item => ({ ...item, is_default: false }))];
        saveDemoCVs();
        feedback('Đã thêm CV vào danh sách demo. Tệp không được gửi lên hay lưu trên máy chủ.');
      } else {
        const data = new FormData();
        data.append('file', file);
        const uploaded = await window.huongApi.request('/students/me/cvs', {
          method: 'POST',
          headers: { Authorization: `Bearer ${sessionStorage.getItem('huong.access') || ''}` },
          body: data,
        });
        cvs = [uploaded, ...cvs];
        renderCVs();
        feedback('Đã tải CV lên thành công.');
      }
    } catch (error) {
      feedback(`Tải CV thất bại: ${error.message}`, true);
    }
  }

  async function runAction(action, id) {
    const cv = cvs.find(item => item.id === id);
    if (!cv) return;
    if (window.huongApi?.isDemo?.()) {
      if (action === 'cv-delete') demoMemory = demoMemory.filter(item => item.id !== id);
      if (action === 'cv-default') demoMemory = demoMemory.map(item => ({ ...item, is_default: item.id === id }));
      if (action === 'cv-parse') return feedback('Phân tích tệp cần backend đang chạy. Bản demo local chỉ lưu thông tin tên tệp.');
      saveDemoCVs();
      return;
    }
    const headers = { Authorization: `Bearer ${sessionStorage.getItem('huong.access') || ''}` };
    try {
      if (action === 'cv-delete') {
        await window.huongApi.request(`/students/me/cvs/${id}`, { method: 'DELETE', headers });
        cvs = cvs.filter(item => item.id !== id);
      } else if (action === 'cv-default') {
        const selected = await window.huongApi.request(`/students/me/cvs/${id}/default`, { method: 'PUT', headers });
        cvs = cvs.map(item => ({ ...item, is_default: item.id === selected.id }));
      } else if (action === 'cv-parse') {
        const parsed = await window.huongApi.request(`/students/me/cvs/${id}/parse`, { method: 'POST', headers });
        cvs = cvs.map(item => item.id === id ? parsed : item);
      }
      renderCVs();
      feedback(action === 'cv-parse' ? 'Đã phân tích CV. Hãy rà soát thông tin trích xuất.' : 'Đã cập nhật danh sách CV.');
    } catch (error) {
      feedback(`Không xử lý được CV: ${error.message}`, true);
    }
  }

  document.addEventListener('change', event => {
    if (event.target.id === 'cv-file-input') {
      upload(event.target.files?.[0]);
      event.target.value = '';
    }
  });
  document.addEventListener('click', event => {
    const button = event.target.closest('[data-cv-default], [data-cv-delete], [data-cv-parse]');
    if (!button) return;
    const action = ['cv-default', 'cv-delete', 'cv-parse'].find(name => button.hasAttribute(`data-${name}`));
    runAction(action, button.dataset[action]);
  });
  document.addEventListener('click', event => {
    if (event.target.closest('[data-view="profile"]')) loadCVs();
  });
})();
