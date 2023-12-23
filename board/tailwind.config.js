module.exports = {
  plugins: [require('daisyui')],
  content: [
    `/components/**/*.{vue,js,ts}`,
    `/pages/**/*.vue`,
    `/composables/**/*.{js,ts}`,
    `/plugins/**/*.{js,ts}`,
    `/app.{js,ts,vue}`,
  ],
}
