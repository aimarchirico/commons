import {describe, expect, it} from 'vitest';
import {
  DOC_ELIGIBLE_VISITORS,
  JSDOC_REQUIRE_KEYS,
  jsdocContexts,
  jsdocRequire,
} from '../comments';

describe('jsdoc configuration mappings', () => {
  it('derives jsdocRequire from JSDOC_REQUIRE_KEYS and DOC_ELIGIBLE_VISITORS', () => {
    const requiredKeys = Object.keys(jsdocRequire);
    expect(requiredKeys).toEqual(
      DOC_ELIGIBLE_VISITORS.filter(type => JSDOC_REQUIRE_KEYS.has(type)),
    );
    for (const key of requiredKeys) {
      expect(jsdocRequire[key]).toBe(true);
    }
  });

  it('derives jsdocContexts as all DOC_ELIGIBLE_VISITORS outside JSDOC_REQUIRE_KEYS', () => {
    expect(jsdocContexts).toEqual(
      DOC_ELIGIBLE_VISITORS.filter(type => !JSDOC_REQUIRE_KEYS.has(type)),
    );
  });

  it('covers all DOC_ELIGIBLE_VISITORS between require and contexts without overlap', () => {
    const requireKeys = Object.keys(jsdocRequire);
    const combined = [...requireKeys, ...jsdocContexts];
    expect(new Set(combined)).toEqual(new Set(DOC_ELIGIBLE_VISITORS));
    expect(combined.length).toBe(DOC_ELIGIBLE_VISITORS.length);
  });
});
