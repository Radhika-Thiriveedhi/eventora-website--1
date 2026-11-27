/**
 * Eventora - Events Helpers
 */

function filterEventsCategory(cat) {
  const url = new URL(window.location.href);
  if (cat) {
    url.searchParams.set('category', cat);
  } else {
    url.searchParams.delete('category');
  }
  window.location.href = url.toString();
}
