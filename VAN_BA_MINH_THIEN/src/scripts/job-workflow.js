(() => {
  const $ = (selector, root = document) => root.querySelector(selector);
  const role = () => window.huongApi?.currentUser?.()?.role || null;
  const headers = () => ({ Authorization: `Bearer ${sessionStorage.getItem('huong.access') || ''}` });
  const notify = message => {
    const toast = $('#toast');
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 2800);
  };
  const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);

  function openCreateForm() {
    if (role() !== 'recruiter') return notify('Chỉ tài khoản nhà tuyển dụng mới được đăng tin.');
    $('#modal-content').innerHTML = `<h2 id="modal-title">Đăng tin tuyển dụng</h2><form id="job-create-form"><label class="form-label">Tên vị trí<input class="form-input" name="title" minlength="3" maxlength="200" required></label><label class="form-label">Mô tả công việc<textarea class="form-input" name="description" rows="5" minlength="20" maxlength="12000" required></textarea></label><div class="form-two"><label class="form-label">Địa điểm<input class="form-input" name="location" value="TP. Hồ Chí Minh" required></label><label class="form-label">Hình thức<select class="form-input" name="employment_type"><option value="internship">Thực tập</option><option value="part_time">Bán thời gian</option><option value="full_time">Toàn thời gian</option><option value="freelance">Freelance</option><option value="remote">Remote</option><option value="hybrid">Hybrid</option></select></label></div><div class="form-two"><label class="form-label">Lương tối thiểu/tháng (VNĐ)<input class="form-input" name="salary_min" type="number" min="0"></label><label class="form-label">Lương tối đa/tháng (VNĐ)<input class="form-input" name="salary_max" type="number" min="0"></label></div><label class="form-label">Kỹ năng <small>Phân cách bằng dấu phẩy</small><input class="form-input" name="skills" placeholder="React, TypeScript"></label><div class="modal-actions"><button type="button" class="button button-outline" id="cancel-edit">Hủy</button><button class="button button-primary" type="submit">Đăng tin</button></div><p id="job-create-feedback" role="status"></p></form>`;
    $('#modal-backdrop').classList.add('open');
  }

  async function submitJob(form) {
    const fields = Object.fromEntries(new FormData(form));
    const payload = {
      title: fields.title.trim(), description: fields.description.trim(), location: fields.location.trim(),
      employment_type: fields.employment_type,
      salary_min: fields.salary_min ? Number(fields.salary_min) : null,
      salary_max: fields.salary_max ? Number(fields.salary_max) : null,
      skills: fields.skills.split(',').map(skill => skill.trim()).filter(Boolean),
    };
    const submit = form.querySelector('[type="submit"]');
    submit.disabled = true;
    try {
      if (window.huongApi?.isDemo?.()) {
        $('#job-create-feedback').textContent = 'Tài khoản demo local không gửi dữ liệu lên máy chủ.';
        return;
      }
      const job = await window.huongApi.request('/jobs', { method: 'POST', headers: headers(), body: JSON.stringify(payload) });
      $('#modal-backdrop').classList.remove('open');
      notify(job.status === 'draft' ? 'Đã lưu tin nháp. Xác minh doanh nghiệp để công khai.' : `Đã đăng tin “${job.title}”.`);
      loadJobs();
      loadRecruiterJobs();
    } catch (error) {
      $('#job-create-feedback').textContent = error.message;
    } finally {
      submit.disabled = false;
    }
  }

  function makeJobCard(job) {
    const card = document.createElement('article');
    card.className = 'job-card';
    card.dataset.serverJob = job.id;
    card.innerHTML = `<div class="job-top"><div class="company-logo logo-teal">${escape((job.company_name || 'C').slice(0, 1))}</div></div><div class="job-copy"><h3>${escape(job.title)}</h3><p class="company-name">${escape(job.company_name)}</p></div><div class="job-meta"><span>${escape(job.location)}</span><span>${escape(job.employment_type)}</span></div><div class="job-tags">${(job.skills || []).map(skill => `<span>${escape(skill)}</span>`).join('')}</div><div class="card-bottom"><span>${job.salary_min || job.salary_max ? `${Number(job.salary_min || 0).toLocaleString('vi-VN')} – ${Number(job.salary_max || 0).toLocaleString('vi-VN')} VNĐ` : 'Thỏa thuận'}</span><span>${escape(job.status)}</span></div>`;
    return card;
  }

  async function loadJobs() {
    if (window.huongApi?.isDemo?.()) return;
    try {
      const jobs = await window.huongApi.request('/jobs');
      let section = $('#server-jobs');
      if (!section) {
        section = document.createElement('section');
        section.id = 'server-jobs';
        section.className = 'job-list server-job-list';
        $('#all-jobs')?.append(section);
      }
      section.replaceChildren(...jobs.map(makeJobCard));
    } catch (error) {
      const section = $('#server-jobs');
      if (section) section.textContent = `Không tải được tin tuyển dụng: ${error.message}`;
    }
  }

  function openServerJob(job) {
    $('#modal-content').innerHTML = `<span class="match-pill"><i></i>${escape(job.company_name)}</span><h2 id="modal-title">${escape(job.title)}</h2><div class="modal-company">${escape(job.location)} · ${escape(job.employment_type)}</div><h3>Mô tả công việc</h3><p>${escape(job.description).replace(/\n/g, '<br>')}</p><h3>Kỹ năng</h3><div class="job-tags">${(job.skills || []).map(skill => `<span>${escape(skill)}</span>`).join('')}</div>${role() === 'student' ? `<button class="button button-primary" data-server-apply="${escape(job.id)}">Ứng tuyển ngay</button>` : ''}`;
    $('#modal-backdrop').classList.add('open');
  }

  async function applyToJob(jobId, button) {
    if (role() !== 'student') return notify('Chỉ tài khoản sinh viên mới được ứng tuyển.');
    if (window.huongApi?.isDemo?.()) return notify('Ứng tuyển vào tin từ máy chủ cần đăng nhập bằng tài khoản máy chủ.');
    button.disabled = true;
    try {
      await window.huongApi.request(`/jobs/${encodeURIComponent(jobId)}/applications`, {
        method: 'POST', headers: headers(), body: JSON.stringify({}),
      });
      button.textContent = 'Đã ứng tuyển';
      notify('Ứng tuyển thành công.');
      loadApplications();
    } catch (error) {
      notify(error.message);
      button.disabled = false;
    }
  }

  async function loadApplications() {
    if (role() !== 'student' || window.huongApi?.isDemo?.()) return;
    try {
      const applications = await window.huongApi.request('/applications/me', { headers: headers() });
      const container = $('#all-applications');
      if (!container) return;
      container.replaceChildren();
      if (!applications.length) { container.textContent = 'Bạn chưa có đơn ứng tuyển.'; return; }
      const list = document.createElement('div');
      list.className = 'applications-list';
      applications.forEach(application => {
        const row = document.createElement('div');
        row.className = 'application-row';
        const job = document.createElement('strong'); job.textContent = application.job_title;
        const company = document.createElement('span'); company.textContent = application.company_name;
        const status = document.createElement('span'); status.textContent = application.status === 'submitted' ? 'Đã nộp' : application.status;
        row.append(job, company, status); list.append(row);
        if (!['rejected', 'withdrawn'].includes(application.status)) {
          const withdraw = document.createElement('button'); withdraw.type = 'button'; withdraw.className = 'button button-outline';
          withdraw.textContent = 'Rút đơn'; withdraw.dataset.withdrawApplication = application.id; row.append(withdraw);
        }
      });
      container.append(list);
    } catch (error) { notify(`Không tải được đơn ứng tuyển: ${error.message}`); }
  }

  async function loadRecruiterJobs() {
    if (role() !== 'recruiter' || window.huongApi?.isDemo?.()) return;
    try {
      const jobs = await window.huongApi.request('/recruiter/jobs', { headers: headers() });
      let section = $('#recruiter-job-list');
      if (!section) {
        section = document.createElement('section');
        section.id = 'recruiter-job-list';
        section.className = 'panel';
        section.innerHTML = '<div class="panel-heading"><div><h2>Tin tuyển dụng của doanh nghiệp</h2></div></div><div class="recruiter-job-items"></div>';
        $('#view-recruiter')?.append(section);
      }
      const items = section.querySelector('.recruiter-job-items');
      items.replaceChildren();
      if (!jobs.length) { items.textContent = 'Doanh nghiệp chưa có tin tuyển dụng.'; return; }
      jobs.forEach(job => {
        const row = document.createElement('div'); row.className = 'application-row';
        const title = document.createElement('strong'); title.textContent = job.title;
        const location = document.createElement('span'); location.textContent = job.location;
        const state = document.createElement('span'); state.textContent = job.status;
        row.dataset.jobRow = job.id;
        row.append(title, location, state);
        if (job.status === 'draft' && job.company_verified) {
          const publish = document.createElement('button'); publish.type = 'button'; publish.className = 'button button-outline'; publish.textContent = 'Công khai'; publish.dataset.publishJob = job.id; row.append(publish);
        } else if (job.status === 'draft') {
          const pending = document.createElement('small'); pending.textContent = 'Chờ xác minh doanh nghiệp để công khai'; row.append(pending);
        }
        if (job.status !== 'closed') {
          const applicants = document.createElement('button'); applicants.type = 'button'; applicants.className = 'button button-outline'; applicants.textContent = 'Đơn ứng tuyển'; applicants.dataset.jobApplicants = job.id; row.append(applicants);
          const close = document.createElement('button'); close.type = 'button'; close.className = 'button button-outline'; close.textContent = 'Đóng tin'; close.dataset.closeJob = job.id; row.append(close);
        }
        items.append(row);
      });
    } catch (error) { notify(`Không tải được tin của doanh nghiệp: ${error.message}`); }
  }

  async function loadJobApplicants(jobId, button) {
    const row = button.closest('[data-job-row]');
    let panel = row.querySelector('.job-applicants');
    if (!panel) { panel = document.createElement('div'); panel.className = 'job-applicants'; row.insertAdjacentElement('afterend', panel); }
    panel.dataset.parentJob = jobId;
    panel.textContent = 'Đang tải hồ sơ ứng tuyển…';
    try {
      const applications = await window.huongApi.request(`/recruiter/jobs/${encodeURIComponent(jobId)}/applications`, { headers: headers() });
      panel.replaceChildren();
      if (!applications.length) { panel.textContent = 'Chưa có đơn ứng tuyển.'; return; }
      applications.forEach(application => {
        const item = document.createElement('div'); item.className = 'application-row';
        const name = document.createElement('strong'); name.textContent = application.student_name;
        const state = document.createElement('span'); state.textContent = application.status;
        item.append(name, state);
        if (application.cv_id) {
          const cv = document.createElement('button'); cv.type = 'button'; cv.className = 'button button-outline'; cv.textContent = 'Tải CV'; cv.dataset.applicantCv = application.id; item.append(cv);
        }
        [['viewed', 'Đánh dấu đã xem'], ['interview', 'Mời phỏng vấn'], ['rejected', 'Từ chối']].forEach(([value, label]) => {
          const action = document.createElement('button'); action.type = 'button'; action.className = 'button button-outline'; action.textContent = label;
          action.dataset.applicationId = application.id; action.dataset.applicationStatus = value; item.append(action);
        });
        panel.append(item);
      });
    } catch (error) { panel.textContent = error.message; }
  }

  async function downloadApplicantCv(applicationId) {
    try {
      const response = await fetch(`${window.location.origin}/api/v1/recruiter/applications/${encodeURIComponent(applicationId)}/cv`, { headers: headers() });
      if (!response.ok) throw new Error((await response.json().catch(() => ({}))).detail || 'Không tải được CV.');
      const blob = await response.blob(); const url = URL.createObjectURL(blob);
      const anchor = document.createElement('a'); anchor.href = url; anchor.download = 'ung-vien-cv'; anchor.click(); URL.revokeObjectURL(url);
    } catch (error) { notify(error.message); }
  }

  document.addEventListener('click', event => {
    const withdraw = event.target.closest('[data-withdraw-application]');
    if (withdraw) {
      event.preventDefault(); event.stopImmediatePropagation();
      window.huongApi.request(`/applications/me/${encodeURIComponent(withdraw.dataset.withdrawApplication)}`, { method: 'DELETE', headers: headers() })
        .then(() => { notify('Đã rút đơn ứng tuyển.'); loadApplications(); })
        .catch(error => notify(error.message));
      return;
    }
    const publish = event.target.closest('[data-publish-job]');
    if (publish) {
      event.preventDefault(); event.stopImmediatePropagation();
      window.huongApi.request(`/jobs/${encodeURIComponent(publish.dataset.publishJob)}/publish`, { method: 'POST', headers: headers(), body: JSON.stringify({}) })
        .then(() => { notify('Tin đã được công khai.'); loadRecruiterJobs(); loadJobs(); }).catch(error => notify(error.message));
      return;
    }
    const close = event.target.closest('[data-close-job]');
    if (close) {
      event.preventDefault(); event.stopImmediatePropagation();
      window.huongApi.request(`/jobs/${encodeURIComponent(close.dataset.closeJob)}`, { method: 'DELETE', headers: headers() })
        .then(() => { notify('Đã đóng tin tuyển dụng.'); loadRecruiterJobs(); loadJobs(); }).catch(error => notify(error.message));
      return;
    }
    const applicants = event.target.closest('[data-job-applicants]');
    if (applicants) { event.preventDefault(); event.stopImmediatePropagation(); loadJobApplicants(applicants.dataset.jobApplicants, applicants); return; }
    const cv = event.target.closest('[data-applicant-cv]');
    if (cv) { event.preventDefault(); event.stopImmediatePropagation(); downloadApplicantCv(cv.dataset.applicantCv); return; }
    const applicationAction = event.target.closest('[data-application-status]');
    if (applicationAction) {
      event.preventDefault(); event.stopImmediatePropagation();
      window.huongApi.request(`/recruiter/applications/${encodeURIComponent(applicationAction.dataset.applicationId)}`, {
        method: 'PATCH', headers: headers(), body: JSON.stringify({ status: applicationAction.dataset.applicationStatus }),
      }).then(() => { notify('Đã cập nhật trạng thái ứng viên.'); const jobId = applicationAction.closest('.job-applicants')?.dataset.parentJob; const button = document.querySelector(`[data-job-row="${jobId}"] [data-job-applicants]`); if (button) loadJobApplicants(jobId, button); })
        .catch(error => notify(error.message));
      return;
    }
    const create = event.target.closest('#create-job');
    if (create) {
      event.preventDefault(); event.stopImmediatePropagation();
      openCreateForm(); return;
    }
    const serverCard = event.target.closest('[data-server-job]');
    if (serverCard) {
      event.preventDefault(); event.stopImmediatePropagation();
      window.huongApi.request(`/jobs`).then(jobs => {
        const job = jobs.find(item => item.id === serverCard.dataset.serverJob);
        if (job) openServerJob(job);
      }).catch(error => notify(error.message));
      return;
    }
    const apply = event.target.closest('[data-server-apply]');
    if (apply) {
      event.preventDefault(); event.stopImmediatePropagation();
      applyToJob(apply.dataset.serverApply, apply);
    }
  }, true);

  document.addEventListener('submit', event => {
    if (event.target.id !== 'job-create-form') return;
    event.preventDefault(); submitJob(event.target);
  });
  document.addEventListener('click', event => {
    if (event.target.closest('[data-view="jobs"]')) loadJobs();
    if (event.target.closest('[data-view="applications"]')) loadApplications();
    if (event.target.closest('[data-view="recruiter"]')) loadRecruiterJobs();
  });
})();
