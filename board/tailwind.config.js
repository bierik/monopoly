module.exports = {
  plugins: [require("daisyui")],
  content: [
    `/components/**/*.{vue,js,ts}`,
    `/pages/**/*.vue`,
    `/layouts/**/*.vue`,
    `/app.vue`,
  ],
  daisyui: {
    themes: ["nord"],
    logs: false,
  },
};
