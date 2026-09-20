import { describe, it, expect } from 'vitest';
import { formatB } from './formatters';

describe('formatB', () => {
  it('formats whole B correctly', () => {
    expect(formatB(25000)).toBe('25');
    expect(formatB(1000)).toBe('1');
    expect(formatB(0)).toBe('0');
  });

  it('formats fractional B correctly', () => {
    expect(formatB(1500)).toBe('1,5');
    expect(formatB(12400)).toBe('12,4');
    expect(formatB(200)).toBe('0,2');
  });

  it('handles +1 B logic correctly', () => {
    // 25 B (25000 units) + 1 B (1000 units)
    expect(formatB(25000 + 1000)).toBe('26');
    // 1.5 B + 1 B
    expect(formatB(1500 + 1000)).toBe('2,5');
  });
});
