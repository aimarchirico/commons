import {describe, expect, it} from 'vitest';
import {isTransform, transform, TRANSFORM_NAMES} from './transforms';

describe('isTransform', () => {
  it('recognises every declared transform name', () => {
    for (const name of TRANSFORM_NAMES) {
      expect(isTransform(name)).toBe(true);
    }
  });

  it('rejects an unknown name', () => {
    expect(isTransform('nope')).toBe(false);
  });
});

describe('transform', () => {
  it('identity leaves the value unchanged', () => {
    expect(transform('identity', 'My Cool App')).toBe('My Cool App');
  });

  it('lower joins words lowercased with no separator', () => {
    expect(transform('lower', 'My Cool App')).toBe('mycoolapp');
  });

  it('kebab joins words lowercased with hyphens', () => {
    expect(transform('kebab', 'My Cool App')).toBe('my-cool-app');
  });

  it('snake joins words lowercased with underscores', () => {
    expect(transform('snake', 'My Cool App')).toBe('my_cool_app');
  });

  it('camel lowercases the first word and capitalizes the rest', () => {
    expect(transform('camel', 'my cool app')).toBe('myCoolApp');
  });

  it('pascal capitalizes every word with no separator', () => {
    expect(transform('pascal', 'my cool app')).toBe('MyCoolApp');
  });

  it('title capitalizes every word separated by spaces', () => {
    expect(transform('title', 'my cool app')).toBe('My Cool App');
  });

  it('path splits dotted identifiers into path segments', () => {
    expect(transform('path', 'no.chirico.template')).toBe(
      'no/chirico/template',
    );
  });

  it('throws naming the transform for an unknown name', () => {
    expect(() => transform('nope', 'value')).toThrow(
      'Unknown transform "nope"',
    );
  });
});
