// app.js: what a framework build sends to every visitor's browser.
// NEXT_PUBLIC_ values are pasted in as plain text.
// Both keys below are FAKE, made for this book.
const config = {
  // from NEXT_PUBLIC_MAPS_KEY: a public, restricted key. Fine.
  mapsKey: "maps_EXAMPLE_NOT_REAL",
  // from NEXT_PUBLIC_STRIPE_SECRET: a secret key. A mistake.
  stripeSecret: "sk_live_EXAMPLE_NOT_REAL",
};

export function checkout(cart) {
  return fetch("https://api.example.invalid/charge", {
    method: "POST",
    headers: { Authorization: "Bearer " + config.stripeSecret },
    body: JSON.stringify(cart),
  });
}
