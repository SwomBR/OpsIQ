import { describe, expect, it } from 'vitest'

import {
  formatCompactCurrency,
  formatCompactNumber,
  formatCurrency,
  formatDate,
  formatDateTime,
  formatDays,
  formatNumber,
  formatPercent,
  humanizeLabel,
} from './format'

describe('number formatting', () => {
  it('adds thousands separators', () => {
    expect(formatNumber(99441)).toBe('99,441')
  })

  it('shortens large numbers', () => {
    expect(formatCompactNumber(96096)).toBe('96.1K')
  })

  it('shows percentages with two decimals', () => {
    expect(formatPercent(97.02)).toBe('97.02%')
    expect(formatPercent(50)).toBe('50.00%')
  })

  it('shows money in Brazilian reais', () => {
    expect(formatCurrency(13591643.7)).toBe('R$13,591,643.70')
    expect(formatCompactCurrency(13591643.7)).toBe('R$13.59M')
  })

  it('shows days with a unit', () => {
    expect(formatDays(9.55)).toBe('9.55 days')
    expect(formatDays(1)).toBe('1.00 day')
  })

  it('shows a dash for missing values instead of NaN or null', () => {
    for (const format of [
      formatNumber,
      formatCompactNumber,
      formatPercent,
      formatCurrency,
      formatDays,
    ]) {
      expect(format(null)).toBe('–')
      expect(format(undefined)).toBe('–')
    }
  })
})

describe('date formatting', () => {
  it('formats API timestamps without shifting the time', () => {
    expect(formatDate('2018-03-15 00:00:00')).toBe('15 Mar 2018')
    expect(formatDateTime('2018-09-19 23:24:07')).toBe('19 Sept 2018, 23:24')
  })

  it('shows a dash for missing or invalid dates', () => {
    expect(formatDate('')).toBe('–')
    expect(formatDate(null)).toBe('–')
    expect(formatDateTime('not a date')).toBe('–')
  })
})

describe('humanizeLabel', () => {
  it('replaces underscores and capitalises the first letter', () => {
    expect(humanizeLabel('credit_card')).toBe('Credit card')
    expect(humanizeLabel('health_beauty')).toBe('Health beauty')
  })

  it('handles empty values', () => {
    expect(humanizeLabel('')).toBe('–')
  })
})
