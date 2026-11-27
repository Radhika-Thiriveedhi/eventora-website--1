/**
 * Eventora - Bookings Helpers
 */

function confirmAction(message, form) {
  if (confirm(message || 'Are you sure you want to proceed?')) {
    form.submit();
  }
  return false;
}
