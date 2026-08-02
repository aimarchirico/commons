import {describe, expect, it} from 'vitest';
import eslintBase from '../eslint-base';
import eslintCore from '../eslint-core';

describe('ESLint configurations', () => {
  it('exports a valid base configuration array', () => {
    expect(eslintBase).toBeDefined();
    expect(Array.isArray(eslintBase)).toBe(true);
    expect(eslintBase.length).toBeGreaterThan(0);
  });

  it('exports a valid core configuration array extending base', () => {
    expect(eslintCore).toBeDefined();
    expect(Array.isArray(eslintCore)).toBe(true);
    expect(eslintCore.length).toBeGreaterThan(eslintBase.length);
  });
});
