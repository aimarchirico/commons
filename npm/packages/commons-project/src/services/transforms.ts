const words = (value: string): string[] => value.match(/[A-Za-z0-9]+/g) ?? [];

const capitalize = (word: string): string =>
  word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();

const TRANSFORMS: Record<string, (value: string) => string> = {
  identity: value => value,
  lower: value =>
    words(value)
      .map(word => word.toLowerCase())
      .join(''),
  kebab: value =>
    words(value)
      .map(word => word.toLowerCase())
      .join('-'),
  snake: value =>
    words(value)
      .map(word => word.toLowerCase())
      .join('_'),
  camel: value =>
    words(value)
      .map((word, index) => (index ? capitalize(word) : word.toLowerCase()))
      .join(''),
  pascal: value => words(value).map(capitalize).join(''),
  title: value => words(value).map(capitalize).join(' '),
  path: value => value.split('.').join('/'),
};

export const TRANSFORM_NAMES = Object.keys(TRANSFORMS);

/**
 * Check if the given string is a valid transform name.
 * @param name The name to check.
 * @returns True if the name is a valid transform, false otherwise.
 */
export const isTransform = (name: string): boolean => name in TRANSFORMS;

/**
 * Apply the specified transform to the value.
 * @param name The name of the transform.
 * @param value The value to transform.
 * @returns The transformed value.
 */
export const transform = (name: string, value: string): string => {
  const fn = TRANSFORMS[name];
  if (!fn) {
    throw new Error(
      `Unknown transform "${name}". Available transforms: ${TRANSFORM_NAMES.join(', ')}.`,
    );
  }
  return fn(value);
};
