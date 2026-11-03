(() => {
  const apiBase = `${window.location.origin}/api/v1`;
  const formIds = ['login-form', 'register-form', 'verify-form', 'forgot-form', 'reset-form'];
  const alertBox = document.getElementById('auth-alert');
  let verifyEmail = '';
  const fallbackDemoAccounts = [
    { role: 'Platform Admin', userRole: 'platform_admin', email: 'admin@huong.local', password: 'AdminDemo2026!' },
    { role: 'Sinh viên', userRole: 'student', email: 'student@huong.local', password: 'StudentDemo2026!' },
    { role: 'Nhà tuyển dụng', userRole: 'recruiter', email: 'recruiter@huong.local', password: 'RecruiterDemo2026!' },
  ];
  let demoAccounts = [...fallbackDemoAccounts];

  function isLocalDemoEnvironment() {
    return window.location.protocol === 'file:' || ['localhost', '127.0.0.1'].includes(window.location.hostname);
  }

  const memorySession = new Map();
  const session = {
    getItem(key) {
      try { return window.sessionStorage.getItem(key); } catch { return memorySession.get(key) ?? null; }
    },
    setItem(key, value) {
      try { window.sessionStorage.setItem(key, value); } catch { memorySession.set(key, String(value)); }
    },
    removeItem(key) {
      try { window.sessionStorage.removeItem(key); } catch { memorySession.delete(key); }
    },
  };

  function showAlert(message, kind = 'error') {
    alertBox.textContent = message;
    alertBox.className = `auth-alert show${kind === 'success' ? ' success' : ''}`;
  }

  function clearAlert() {
    alertBox.textContent = '';
    alertBox.className = 'auth-alert';
  }

  function getErrorMessage(body, response) {
    if (Array.isArray(body?.detail)) return body.detail.map(x => x.msg).join('. ');
    return body?.detail || body?.message || `Có lỗi xảy ra (${response.status}).`;
  }

  async function request(path, options = {}) {
    let response;
    const headers = { ...(options.headers || {}) };
    if (!(options.body instanceof FormData)) headers['Content-Type'] = 'application/json';
    try {
      response = await fetch(`${apiBase}${path}`, {
        ...options,
        headers,
      });
    } catch {
      throw new Error('Không kết nối được máy chủ. Hãy khởi động backend và mở ứng dụng tại http://localhost:8000.');
    }
    const body = response.status === 204 ? null : await response.json().catch(() => ({}));
    if (!response.ok) {
      const error = new Error(getErrorMessage(body, response));
      error.status = response.status;
      throw error;
    }
    return body;
  }

  function formData(form) {
    return Object.fromEntries(new FormData(form).entries());
  }

  async function loadDemoAccounts() {
    const panel = document.getElementById('demo-accounts');
    const list = document.getElementById('demo-account-list');
    const renderAccounts = accounts => {
      list.replaceChildren();
      accounts.forEach((account, index) => {
        const row = document.createElement('div');
        row.className = 'demo-account-row';
        const info = document.createElement('span');
        const role = document.createElement('strong');
        role.textContent = account.role;
        const email = document.createElement('small');
        email.textContent = `${account.email} · ${account.password}`;
        info.append(role, email);
        const use = document.createElement('button');
        use.type = 'button';
        use.textContent = 'Điền';
        use.dataset.demoAccount = String(index);
        row.append(info, use);
        list.append(row);
      });
    };
    if (isLocalDemoEnvironment()) {
      demoAccounts = [...fallbackDemoAccounts];
      renderAccounts(demoAccounts);
      document.getElementById('demo-notice').textContent = 'Bản demo local để xem giao diện. Dữ liệu không lưu lên máy chủ.';
      panel.hidden = false;
    }
    try {
      const result = await request('/system/demo-accounts');
      if (result.environment !== 'development' || !Array.isArray(result.accounts)) return;
      demoAccounts = result.accounts.map((account, index) => ({ ...account, userRole: fallbackDemoAccounts[index]?.userRole }));
      renderAccounts(demoAccounts);
      document.getElementById('demo-notice').textContent = result.notice || '';
      panel.hidden = false;
    } catch {
      if (!isLocalDemoEnvironment()) panel.hidden = true;
    }
  }

  function setBusy(form, busy, label) {
    const button = form.querySelector('[type="submit"]');
    if (!button) return;
    if (busy) {
      button.dataset.original = button.textContent;
      button.disabled = true;
      button.textContent = label || 'Đang xử lý…';
    } else {
      button.disabled = false;
      button.textContent = button.dataset.original || 'Tiếp tục';
    }
  }

  function showAuthView(view) {
    clearAlert();
    formIds.forEach(id => document.getElementById(id).classList.toggle('hidden', id !== `${view}-form`));
    document.querySelectorAll('.auth-tab').forEach(tab => {
      const active = tab.dataset.authView === view && ['login', 'register'].includes(view);
      tab.classList.toggle('active', active);
      tab.hidden = !['login', 'register'].includes(view);
    });
    const titles = {
      login: ['Chào mừng bạn trở lại', 'Đăng nhập để tiếp tục hành trình nghề nghiệp của bạn.'],
      register: ['Tạo tài khoản Hướng', 'Bắt đầu kết nối với cơ hội phù hợp dành cho bạn.'],
      verify: ['Xác minh email', 'Chỉ còn một bước để kích hoạt tài khoản của bạn.'],
      forgot: ['Lấy lại quyền truy cập', 'Chúng tôi sẽ gửi hướng dẫn đặt lại mật khẩu tới email của bạn.'],
      reset: ['Chọn mật khẩu mới', 'Đặt mật khẩu mới để tiếp tục sử dụng Hướng.'],
    }[view];
    document.getElementById('auth-title').textContent = titles[0];
    document.getElementById('auth-subtitle').textContent = titles[1];
  }

  async function enterApp(tokens, user, demoMode = false) {
    session.setItem('huong.access', tokens.access_token);
    session.setItem('huong.refresh', tokens.refresh_token);
    session.setItem('huong.user', JSON.stringify(user));
    if (demoMode) session.setItem('huong.demo-mode', 'true');
    else session.removeItem('huong.demo-mode');
    document.body.classList.add('authenticated');
    document.getElementById('signed-in-name').textContent = user.full_name;
    const sidebarName = document.querySelector('.account-copy strong');
    const sidebarRole = document.querySelector('.account-copy small');
    if (sidebarName) sidebarName.textContent = user.full_name;
    if (sidebarRole) {
      const roleLabels = {
        student: user.status === 'demo' ? 'Sinh viên · Demo local' : 'Sinh viên · Đã xác minh email',
        recruiter: user.status === 'demo' ? 'Nhà tuyển dụng · Demo local' : 'Nhà tuyển dụng · Chờ xác minh công ty',
        platform_admin: user.status === 'demo' ? 'Quản trị viên · Demo local' : 'Quản trị viên',
      };
      sidebarRole.textContent = roleLabels[user.role] || user.role;
    }
    const profileName = document.querySelector('#view-profile .profile-hero h2');
    if (profileName) profileName.textContent = user.full_name;
    const isRecruiter = user.role === 'recruiter';
    const isAdmin = user.role === 'platform_admin';
    document.getElementById('workspace-name').textContent = isAdmin ? 'Quản trị hệ thống' : isRecruiter ? 'Không gian nhà tuyển dụng' : 'Không gian sinh viên';
    document.querySelectorAll('.primary-nav [data-view]').forEach(item => {
      item.hidden = isAdmin ? item.dataset.view !== 'admin' : isRecruiter ? !['recruiter'].includes(item.dataset.view) : ['recruiter', 'admin'].includes(item.dataset.view);
    });
    const adminName = document.getElementById('admin-name');
    if (adminName) adminName.textContent = user.full_name;
    window.navigate?.(isAdmin ? 'admin' : isRecruiter ? 'recruiter' : 'home');
  }

  async function loadExistingSession() {
    if (session.getItem('huong.demo-mode') === 'true') {
      const demoUser = JSON.parse(session.getItem('huong.user') || 'null');
      if (demoUser) {
        await enterApp({ access_token: 'local-demo', refresh_token: 'local-demo' }, demoUser, true);
        return;
      }
    }
    let access = session.getItem('huong.access');
    let refresh = session.getItem('huong.refresh');
    if (!access && !refresh) return;
    try {
      let user;
      try {
        user = await request('/auth/me', { headers: { Authorization: `Bearer ${access}` } });
      } catch (error) {
        if (!refresh) throw error;
        const tokens = await request('/auth/refresh', { method: 'POST', body: JSON.stringify({ refresh_token: refresh }) });
        access = tokens.access_token;
        refresh = tokens.refresh_token;
        session.setItem('huong.access', access);
        session.setItem('huong.refresh', refresh);
        user = await request('/auth/me', { headers: { Authorization: `Bearer ${access}` } });
      }
      await enterApp({ access_token: access, refresh_token: refresh }, user);
    } catch {
      session.removeItem('huong.access');
      session.removeItem('huong.refresh');
      session.removeItem('huong.user');
      session.removeItem('huong.demo-mode');
      showAuthView('login');
    }
  }

  document.addEventListener('click', event => {
    const demo = event.target.closest('[data-demo-account]');
    if (demo) {
      const account = demoAccounts[Number(demo.dataset.demoAccount)];
      if (account) {
        document.querySelector('#login-form [name="email"]').value = account.email;
        document.querySelector('#login-form [name="password"]').value = account.password;
        showAlert(`Đã điền tài khoản ${account.role}.`, 'success');
      }
      return;
    }
    const tab = event.target.closest('[data-auth-view]');
    if (tab) {
      event.preventDefault();
      showAuthView(tab.dataset.authView);
    }
  });

  document.getElementById('login-form').addEventListener('submit', async event => {
    event.preventDefault();
    const form = event.currentTarget;
    setBusy(form, true, 'Đang đăng nhập…');
    clearAlert();
    try {
      const data = formData(form);
      const tokens = await request('/auth/login', { method: 'POST', body: JSON.stringify(data) });
      const user = await request('/auth/me', { headers: { Authorization: `Bearer ${tokens.access_token}` } });
      await enterApp(tokens, user);
    } catch (error) {
      const data = formData(form);
      const demoAccount = demoAccounts.find(account => account.email === data.email && account.password === data.password);
      if (demoAccount && isLocalDemoEnvironment()) {
        const localUser = {
          id: `local-${demoAccount.userRole}`,
          email: demoAccount.email,
          full_name: demoAccount.userRole === 'platform_admin' ? 'Hướng Platform Admin' : demoAccount.userRole === 'student' ? 'Nguyễn Minh Anh' : 'Trần Gia Huy',
          role: demoAccount.userRole,
          status: 'demo',
        };
        await enterApp({ access_token: 'local-demo', refresh_token: 'local-demo' }, localUser, true);
        window.toast?.('Bạn đang ở chế độ demo local; dữ liệu không lưu lên máy chủ.');
        return;
      }
      showAlert(error.message);
    } finally {
      setBusy(form, false);
    }
  });

  document.getElementById('register-form').addEventListener('submit', async event => {
    event.preventDefault();
    const form = event.currentTarget;
    setBusy(form, true, 'Đang tạo tài khoản…');
    clearAlert();
    try {
      const data = formData(form);
      data.accept_terms = new FormData(form).has('accept_terms');
      data.accept_data_processing = new FormData(form).has('accept_data_processing');
      if (data.role !== 'recruiter') {
        delete data.company_name;
        delete data.tax_code;
        delete data.job_title;
      }
      verifyEmail = data.email;
      await request('/auth/register', { method: 'POST', body: JSON.stringify(data) });
      document.querySelector('#verify-form [name="email"]').value = verifyEmail;
      showAuthView('verify');
      showAlert('Đã tạo tài khoản. Nhập token trong email xác minh để kích hoạt.', 'success');
    } catch (error) {
      showAlert(error.message);
    } finally {
      setBusy(form, false);
    }
  });

  document.getElementById('verify-form').addEventListener('submit', async event => {
    event.preventDefault();
    const form = event.currentTarget;
    setBusy(form, true, 'Đang xác minh…');
    clearAlert();
    try {
      const data = formData(form);
      await request('/auth/verify-email', { method: 'POST', body: JSON.stringify({ token: data.token.trim() }) });
      document.querySelector('#login-form [name="email"]').value = data.email;
      showAuthView('login');
      showAlert('Email đã xác minh. Bạn có thể đăng nhập.', 'success');
    } catch (error) {
      showAlert(error.message);
    } finally {
      setBusy(form, false);
    }
  });

  document.getElementById('resend-verification').addEventListener('click', async () => {
    const email = document.querySelector('#verify-form [name="email"]').value.trim();
    if (!email) return showAlert('Nhập email trước khi gửi lại.');
    try {
      await request('/auth/resend-verification', { method: 'POST', body: JSON.stringify({ email }) });
      showAlert('Nếu tài khoản đang chờ xác minh, email mới sẽ được gửi. Hãy kiểm tra hộp thư.', 'success');
    } catch (error) {
      showAlert(error.message);
    }
  });

  document.getElementById('forgot-form').addEventListener('submit', async event => {
    event.preventDefault();
    const form = event.currentTarget;
    setBusy(form, true, 'Đang gửi…');
    try {
      const data = formData(form);
      await request('/auth/forgot-password', { method: 'POST', body: JSON.stringify(data) });
      document.querySelector('#reset-form [name="token"]').value = '';
      showAuthView('reset');
      showAlert('Nếu email hợp lệ, token đặt lại đã được gửi. Hãy kiểm tra hộp thư.', 'success');
    } catch (error) {
      showAlert(error.message);
    } finally {
      setBusy(form, false);
    }
  });

  document.getElementById('reset-form').addEventListener('submit', async event => {
    event.preventDefault();
    const form = event.currentTarget;
    setBusy(form, true, 'Đang cập nhật…');
    try {
      const data = formData(form);
      await request('/auth/reset-password', { method: 'POST', body: JSON.stringify({ token: data.token.trim(), new_password: data.new_password }) });
      showAuthView('login');
      showAlert('Mật khẩu đã được cập nhật. Hãy đăng nhập bằng mật khẩu mới.', 'success');
    } catch (error) {
      showAlert(error.message);
    } finally {
      setBusy(form, false);
    }
  });

  document.getElementById('logout-button').addEventListener('click', async () => {
    const refreshToken = session.getItem('huong.refresh');
    if (refreshToken) {
      try { await request('/auth/logout', { method: 'POST', body: JSON.stringify({ refresh_token: refreshToken }) }); } catch { /* Local session is still cleared. */ }
    }
    session.removeItem('huong.access');
    session.removeItem('huong.refresh');
    session.removeItem('huong.user');
    session.removeItem('huong.demo-mode');
    document.body.classList.remove('authenticated');
    document.getElementById('logout-button').classList.remove('open');
    showAuthView('login');
  });

  document.getElementById('profile-menu-button').addEventListener('click', () => {
    document.getElementById('logout-button').classList.toggle('open');
  });

  const registerRole = document.getElementById('register-role');
  const companyFields = document.getElementById('company-signup-fields');
  function toggleCompanyFields() {
    const enabled = registerRole.value === 'recruiter';
    companyFields.hidden = !enabled;
    companyFields.querySelectorAll('input').forEach(input => { input.required = enabled; });
  }
  registerRole.addEventListener('change', toggleCompanyFields);
  toggleCompanyFields();

  window.huongApi = {
    request,
    isDemo: () => session.getItem('huong.demo-mode') === 'true',
    currentUser: () => JSON.parse(session.getItem('huong.user') || 'null'),
  };

  showAuthView('login');
  loadDemoAccounts();
  loadExistingSession();
})();
