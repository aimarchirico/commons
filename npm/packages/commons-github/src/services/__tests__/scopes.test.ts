import {describe, expect, it} from 'vitest';
import {parseEnvironmentScopes, parseNames} from '../scopes.js';

describe('parseEnvironmentScopes', () => {
  it('parses a multi-environment scope list', () => {
    expect(
      parseEnvironmentScopes(
        'web-production=APP_URL,ACCOUNT_ID;api-production=VPS_HOST',
      ),
    ).toEqual([
      {environment: 'web-production', names: ['APP_URL', 'ACCOUNT_ID']},
      {environment: 'api-production', names: ['VPS_HOST']},
    ]);
  });

  it('returns an empty array for undefined input', () => {
    expect(parseEnvironmentScopes(undefined)).toEqual([]);
  });

  it('drops groups with no names', () => {
    expect(parseEnvironmentScopes('empty-env=')).toEqual([]);
  });

  it('throws on a malformed group missing "="', () => {
    expect(() => parseEnvironmentScopes('malformed')).toThrow(
      'Malformed environment scope',
    );
  });
});

describe('parseNames', () => {
  it('splits on commas and whitespace', () => {
    expect(parseNames('A, B  C,D')).toEqual(['A', 'B', 'C', 'D']);
  });

  it('returns an empty array for undefined input', () => {
    expect(parseNames(undefined)).toEqual([]);
  });
});
