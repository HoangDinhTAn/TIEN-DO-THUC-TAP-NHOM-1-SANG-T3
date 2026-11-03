(() => {
  const $ = (selector, root = document) => root.querySelector(selector);
  const localKey = 'huong-demo-company';
  let demoCompany;

  function demoData() {
    if (demoCompany) return demoCompany;
    try { demoCompany = JSON.parse(localStorage.getItem(localKey) || 'null'); } catch { demoCompany = null; }
    if (!demoCompany) demoCompany = { id: 'demo-company', name: 'Mây Studio (Demo)', tax_code: '9900000001', industry: 'Công nghệ thông tin', verification_status: 'pending', verification_note: null, documents: [] };
    return demoCompany;
  }

  function saveDemoCompany() {
    try { localStorage.setItem(localKey, JSON.stringify(demoCompany)); } catch { /* Keep the demo verification in memory for this tab. */ }
  }

  function statusName(status) {
    return ({ pending: 'Chờ xác minh', verified: 'Đã xác minh', rejected: 'Cần bổ sung giấy tờ' })[status] || status;
  }

  function ensureRecruiterPanel() {
    if ($('#company-verification-panel')) return;
    const view = $('#view-recruiter');
    const heading = view?.querySelector('.page-heading');
    if (!view || !heading) return;
    const panel = document.createElement('section');
    panel.id = 'company-verification-panel';
    panel.className = 'panel company-verification-panel';
    panel.innerHTML = '<div class="company-panel-info"><div class="company-panel-icon">▣</div><div class="company-panel-copy"><span class="eyebrow">HỒ SƠ DOANH NGHIỆP</span><h2 id="company-panel-name">Đang tải công ty…</h2><p id="company-panel-meta"></p></div><span id="company-status" class="company-status"></span></div><p id="company-review-note" class="company-review-note"></p><div class="company-docs-row"><div><strong>Giấy tờ xác minh</strong><small>PDF, PNG hoặc JPG · tối đa 10 MB</small></div><label class="button button-outline company-doc-upload" for="company-doc-input">＋ Tải giấy tờ</label><input id="company-doc-input" type="file" accept=".pdf,.png,.jpg,.jpeg,application/pdf,image/png,image/jpeg" hidden></div><div id="company-doc-list" class="company-doc-list"></div><div id="company-feedback" class="company-feedback" role="status"></div>';
    heading.insertAdjacentElement('afterend', panel);
  }

  function renderCompany(company) {
    ensureRecruiterPanel();
    $('#company-panel-name').textContent = company.name || 'Chưa có tên công ty';
    $('#company-panel-meta').textContent = `MST ${company.tax_code || '—'}${company.industry ? ` · ${company.industry}` : ''}`;
    const status = $('#company-status');
    status.textContent = statusName(company.verification_status);
    status.className = `company-status ${company.verification_status}`;
    $('#company-review-note').textContent = company.verification_note || (company.verification_status === 'verified' ? 'Doanh nghiệp đã được xác minh; tin tuyển dụng có thể gửi duyệt.' : 'Doanh nghiệp cần được admin xác minh trước khi đăng tin công khai.');
    const list = $('#company-doc-list');
    list.replaceChildren();
    (company.documents || []).forEach(doc => {
      const row = document.createElement('div');
      row.className = 'company-doc-item';
      const filename = document.createElement('span');
      filename.textContent = doc.original_name;
      const docStatus = document.createElement('small');
      docStatus.textContent = doc.status === 'approved' ? 'Đã duyệt' : doc.status === 'rejected' ? 'Bị từ chối' : 'Chờ duyệt';
      row.append(filename, docStatus);
      list.append(row);
    });
  }

  async function loadCompany() {
    ensureRecruiterPanel();
    if (!$('#company-verification-panel')) return;
    if (window.huongApi?.isDemo?.()) {
      renderCompany(demoData());
      return;
    }
    try {
      const headers = { Authorization: `Bearer ${sessionStorage.getItem('huong.access') || ''}` };
      const [company, documents] = await Promise.all([
        window.huongApi.request('/companies/me', { headers }),
        window.huongApi.request('/companies/me/documents', { headers }),
      ]);
      renderCompany({ ...company, documents });
    } catch (error) {
      $('#company-feedback').textContent = `Không tải được hồ sơ công ty: ${error.message}`;
    }
  }

  function ensureAdminQueue() {
    if ($('#admin-company-queue')) return;
    const view = $('#view-admin');
    const roadmap = view?.querySelector('.admin-roadmap');
    if (!view || !roadmap) return;
    const section = document.createElement('section');
    section.id = 'admin-company-queue';
    section.className = 'panel admin-company-queue';
    section.innerHTML = '<div class="panel-heading"><div><h2>Hàng chờ xác minh doanh nghiệp</h2><p>Kiểm tra hồ sơ và giấy tờ trước khi cho phép đăng tin.</p></div><button class="link-button" id="refresh-company-queue">Làm mới ↻</button></div><div id="pending-company-list" class="pending-company-list"></div><div id="admin-company-feedback" class="company-feedback" role="status"></div>';
    view.insertBefore(section, roadmap);
  }

  function renderPending(companies) {
    ensureAdminQueue();
    const list = $('#pending-company-list');
    list.replaceChildren();
    if (!companies.length) {
      const empty = document.createElement('div');
      empty.className = 'cv-empty';
      empty.textContent = 'Hiện chưa có doanh nghiệp chờ duyệt.';
      list.append(empty);
      return;
    }
    companies.forEach(company => {
      const card = document.createElement('article');
      card.className = 'pending-company-card';
      const header = document.createElement('div');
      header.className = 'pending-company-header';
      const identity = document.createElement('div');
      const name = document.createElement('h3');
      name.textContent = company.name;
      const tax = document.createElement('small');
      tax.textContent = `MST ${company.tax_code} · ${company.industry || 'Chưa khai báo ngành'}`;
      identity.append(name, tax);
      const date = document.createElement('span');
      date.className = 'pending-date';
      date.textContent = 'Chờ xác minh';
      header.append(identity, date);
      card.append(header);
      (company.members || []).forEach(member => {
        const contact = document.createElement('p');
        contact.className = 'pending-contact';
        contact.textContent = `${member.name} · ${member.email} · ${member.title}`;
        card.append(contact);
      });
      const docs = document.createElement('div');
      docs.className = 'pending-docs';
      (company.documents || []).forEach(doc => {
        const docRow = document.createElement('div');
        docRow.className = 'pending-doc-row';
        const docName = document.createElement('span');
        docName.textContent = `${doc.original_name} · ${(doc.size_bytes / 1024 / 1024).toFixed(2)} MB`;
        const download = document.createElement('button');
        download.type = 'button';
        download.className = 'cv-action';
        download.textContent = 'Tải để xem';
        download.dataset.documentDownload = `${company.id}:${doc.id}`;
        docRow.append(docName, download);
        docs.append(docRow);
      });
      if (!(company.documents || []).length) {
        const noDoc = document.createElement('p');
        noDoc.className = 'pending-no-doc';
        noDoc.textContent = 'Chưa nộp giấy tờ. Chưa thể xác minh công ty.';
        docs.append(noDoc);
      }
      card.append(docs);
      const actions = document.createElement('div');
      actions.className = 'pending-company-actions';
      const reject = document.createElement('button');
      reject.type = 'button';
      reject.className = 'button button-outline reject-company';
      reject.textContent = 'Yêu cầu bổ sung / Từ chối';
      reject.dataset.rejectCompany = company.id;
      const approve = document.createElement('button');
      approve.type = 'button';
      approve.className = 'button button-primary';
      approve.textContent = 'Xác minh doanh nghiệp';
      approve.dataset.approveCompany = company.id;
      approve.disabled = !(company.documents || []).length;
      actions.append(reject, approve);
      card.append(actions);
      list.append(card);
    });
  }

  async function loadPendingCompanies() {
    ensureAdminQueue();
    if (window.huongApi?.isDemo?.()) {
      const company = demoData();
      renderPending(company.verification_status === 'pending' ? [{ ...company, members: [{ name: 'Trần Gia Huy', email: 'recruiter@huong.local', title: 'Recruiter' }] }] : []);
      return;
    }
    try {
      const companies = await window.huongApi.request('/admin/companies/pending', { headers: { Authorization: `Bearer ${sessionStorage.getItem('huong.access') || ''}` } });
      renderPending(companies);
    } catch (error) {
      const feedback = $('#admin-company-feedback');
      if (feedback) feedback.textContent = `Không tải được hàng chờ: ${error.message}`;
    }
  }

  async function uploadCompanyDocument(file) {
    if (!file) return;
    if (file.size > 10 * 1024 * 1024) return $('#company-feedback').textContent = 'Giấy tờ tối đa 10 MB.';
    if (!/\.(pdf|png|jpe?g)$/i.test(file.name)) return $('#company-feedback').textContent = 'Chỉ nhận PDF, PNG hoặc JPG.';
    if (window.huongApi?.isDemo?.()) {
      const company = demoData();
      company.documents = [{ id: `demo-doc-${Date.now()}`, original_name: file.name, size_bytes: file.size, status: 'pending' }, ...(company.documents || [])];
      company.verification_status = 'pending';
      saveDemoCompany();
      renderCompany(company);
      $('#company-feedback').textContent = 'Đã thêm giấy tờ vào bản demo. Tệp không được gửi lên máy chủ.';
      return;
    }
    const data = new FormData();
    data.append('file', file);
    try {
      await window.huongApi.request('/companies/me/documents', { method: 'POST', headers: { Authorization: `Bearer ${sessionStorage.getItem('huong.access') || ''}` }, body: data });
      $('#company-feedback').textContent = 'Đã tải giấy tờ lên. Hồ sơ đang chờ admin xem xét.';
      loadCompany();
    } catch (error) {
      $('#company-feedback').textContent = `Không tải được giấy tờ: ${error.message}`;
    }
  }

  async function reviewCompany(companyId, action) {
    if (window.huongApi?.isDemo?.()) {
      const company = demoData();
      if (action === 'approve' && !(company.documents || []).length) return $('#admin-company-feedback').textContent = 'Hãy thêm giấy tờ ở tài khoản nhà tuyển dụng trước khi duyệt.';
      const note = action === 'reject' ? window.prompt('Ghi rõ lý do cần bổ sung giấy tờ:') : '';
      if (action === 'reject' && !note) return;
      company.verification_status = action === 'approve' ? 'verified' : 'rejected';
      company.verification_note = note || null;
      company.documents = (company.documents || []).map(doc => ({ ...doc, status: action === 'approve' ? 'approved' : 'rejected' }));
      saveDemoCompany();
      await loadPendingCompanies();
      $('#admin-company-feedback').textContent = action === 'approve' ? 'Đã xác minh công ty trong bản demo.' : 'Đã yêu cầu bổ sung trong bản demo.';
      return;
    }
    let note = '';
    if (action === 'reject') {
      note = window.prompt('Ghi lý do từ chối hoặc giấy tờ cần bổ sung:') || '';
      if (note.trim().length < 4) return;
    }
    const headers = { Authorization: `Bearer ${sessionStorage.getItem('huong.access') || ''}` };
    try {
      await window.huongApi.request(`/admin/companies/${companyId}/${action}`, { method: 'POST', headers, body: JSON.stringify({ note }) });
      await loadPendingCompanies();
      $('#admin-company-feedback').textContent = action === 'approve' ? 'Doanh nghiệp đã được xác minh.' : 'Đã ghi nhận yêu cầu bổ sung/từ chối.';
    } catch (error) {
      $('#admin-company-feedback').textContent = `Không xử lý được hồ sơ: ${error.message}`;
    }
  }

  async function downloadDocument(value) {
    const [companyId, documentId] = value.split(':');
    if (window.huongApi?.isDemo?.()) return $('#admin-company-feedback').textContent = 'Tệp bản demo không được tải lên máy chủ.';
    try {
      const response = await fetch(`${window.location.origin}/api/v1/admin/companies/${companyId}/documents/${documentId}`, { headers: { Authorization: `Bearer ${sessionStorage.getItem('huong.access') || ''}` } });
      if (!response.ok) throw new Error('Không tải được giấy tờ.');
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = 'company-verification-document';
      anchor.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      $('#admin-company-feedback').textContent = error.message;
    }
  }

  document.addEventListener('change', event => {
    if (event.target.id === 'company-doc-input') {
      uploadCompanyDocument(event.target.files?.[0]);
      event.target.value = '';
    }
  });
  document.addEventListener('click', event => {
    const approve = event.target.closest('[data-approve-company]');
    const reject = event.target.closest('[data-reject-company]');
    const download = event.target.closest('[data-document-download]');
    if (approve) reviewCompany(approve.dataset.approveCompany, 'approve');
    if (reject) reviewCompany(reject.dataset.rejectCompany, 'reject');
    if (download) downloadDocument(download.dataset.documentDownload);
    if (event.target.closest('#refresh-company-queue')) loadPendingCompanies();
  });
  document.addEventListener('click', event => {
    if (event.target.closest('[data-view="recruiter"]')) loadCompany();
    if (event.target.closest('[data-view="admin"]')) loadPendingCompanies();
  });
})();
