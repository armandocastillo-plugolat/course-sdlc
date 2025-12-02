module.exports = {
  testEnvironment: 'node',
  testMatch: ['**/tests/**/*.test.js', '**/__tests__/**/*.js'],
  collectCoverageFrom: [
    '**/*.{js,jsx}',
    '!**/node_modules/**',
    '!**/tests/**',
    '!jest.config.js'
  ],
  coverageDirectory: 'coverage',
  verbose: true,
  testTimeout: 10000
};