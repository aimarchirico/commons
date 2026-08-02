import {describe, expect, it} from 'vitest';
import vitestBase from '../vitest-base';

describe('Vitest configuration', () => {
  it('exports a valid vitest base configuration', () => {
    expect(vitestBase).toBeDefined();
    expect(vitestBase.test?.coverage?.enabled).toBe(true);
    expect(vitestBase.test?.coverage?.provider).toBe('v8');
  });
});
