(() => {
  const userRole = () => window.huongApi?.currentUser?.()?.role || null;
  const allowedViews = {
    student: new Set(['home', 'jobs', 'applications', 'saved', 'profile']),
    recruiter: new Set(['recruiter']),
    platform_admin: new Set(['admin']),
    moderator: new Set(['admin']),
  };
  const toast = message => {
    const element = document.getElementById('toast');
    if (!element) return;
    element.textContent = message;
    element.classList.add('show');
    window.setTimeout(() => element.classList.remove('show'), 2600);
  };

  function updateApplicationActions() {
    if (userRole() !== 'recruiter') return;
    document.querySelectorAll('[data-apply]').forEach(button => {
      if (button.disabled && button.textContent === 'Chỉ sinh viên được ứng tuyển') return;
      button.disabled = true;
      button.textContent = 'Chỉ sinh viên được ứng tuyển';
      button.setAttribute('aria-label', 'Nhà tuyển dụng không thể ứng tuyển');
    });
  }

  const originalNavigate = window.navigate;
  if (typeof originalNavigate === 'function') {
    window.navigate = view => {
      if (!allowedViews[userRole()]?.has(view)) {
        toast('Tài khoản của bạn không có quyền mở mục này.');
        return;
      }
      originalNavigate(view);
    };
  }

  document.addEventListener('click', event => {
    const role = userRole();
    const target = event.target.closest('[data-view], #create-job, [data-apply], [data-invite]');
    if (!target) return;

    if (target.matches('#create-job') && role !== 'recruiter') {
      event.preventDefault();
      event.stopImmediatePropagation();
      toast('Chỉ tài khoản nhà tuyển dụng mới được đăng tin tuyển dụng.');
      return;
    }
    if (target.matches('[data-apply]') && role !== 'student') {
      event.preventDefault();
      event.stopImmediatePropagation();
      toast('Chỉ tài khoản sinh viên mới được ứng tuyển công việc.');
      return;
    }
    if (target.matches('[data-view]') && !allowedViews[role]?.has(target.dataset.view)) {
      event.preventDefault();
      event.stopImmediatePropagation();
      toast('Tài khoản của bạn không có quyền mở mục này.');
      return;
    }
    if (target.matches('[data-invite]') && role !== 'recruiter') {
      event.preventDefault();
      event.stopImmediatePropagation();
      toast('Chỉ tài khoản nhà tuyển dụng mới được mời ứng viên.');
    }
  }, true);

  new MutationObserver(updateApplicationActions).observe(document.body, { childList: true, subtree: true });
  document.addEventListener('DOMContentLoaded', updateApplicationActions);
  updateApplicationActions();
})();
