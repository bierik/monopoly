import withNuxt from "./.nuxt/eslint.config.mjs";
import tailwind from "eslint-plugin-tailwindcss";

export default withNuxt(tailwind.configs["flat/recommended"], {
  rules: {
    "vue/no-multiple-template-root": "off",
    "vue/multi-word-component-names": "off",
    "vue/html-self-closing": [
      "off",
      {
        html: {
          normal: "never",
          void: "always",
        },
      },
    ],
  },
});
