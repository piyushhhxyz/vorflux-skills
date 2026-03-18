/**
 * Jest/Vitest test template
 * Run: npx jest --coverage   OR   npx vitest run --coverage
 */

// import { myFunction, MyClass } from './module';

// ── Mocks ─────────────────────────────────────────────────────────────────────

jest.mock('./dependency', () => ({
  externalCall: jest.fn().mockResolvedValue({ data: 'mocked' }),
}));

const mockFetch = jest.fn();
global.fetch = mockFetch;

// ── Setup / teardown ──────────────────────────────────────────────────────────

beforeEach(() => {
  jest.clearAllMocks();
});

afterAll(() => {
  jest.restoreAllMocks();
});

// ── Unit tests ────────────────────────────────────────────────────────────────

describe('myFunction', () => {
  it('returns expected value for valid input', () => {
    // const result = myFunction('valid');
    // expect(result).toBe('expected');
  });

  it('throws TypeError for null input', () => {
    // expect(() => myFunction(null)).toThrow(TypeError);
  });

  it('throws for empty string', () => {
    // expect(() => myFunction('')).toThrow();
  });

  it.each([
    ['input1', 'expected1'],
    ['input2', 'expected2'],
    [0,        null],
  ])('handles %s → %s', (input, expected) => {
    // expect(myFunction(input)).toBe(expected);
  });
});

// ── Async tests ───────────────────────────────────────────────────────────────

describe('myAsyncFunction', () => {
  it('resolves with correct data', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: 1, name: 'test' }),
    });
    // const result = await myAsyncFunction('arg');
    // expect(result).toEqual({ id: 1, name: 'test' });
  });

  it('rejects when API fails', async () => {
    mockFetch.mockResolvedValueOnce({ ok: false, status: 500 });
    // await expect(myAsyncFunction('arg')).rejects.toThrow();
  });
});

// ── Class tests ───────────────────────────────────────────────────────────────

describe('MyClass', () => {
  let instance;

  beforeEach(() => {
    // instance = new MyClass({ config: 'value' });
  });

  it('initializes with correct defaults', () => {
    // expect(instance.property).toBe(defaultValue);
  });

  it('method returns expected result', () => {
    // expect(instance.method('arg')).toBe('expected');
  });
});
