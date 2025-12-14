const numberFormatter = new Intl.NumberFormat("de-CH");

export function toCurrency(value = 0) {
  return `${numberFormatter.format(value || 0)} M`;
}
