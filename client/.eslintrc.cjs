/* eslint-env node */
module.exports = {
  root: true,
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
    ecmaFeatures: { jsx: true },
    project: null
  },
  settings: {
    react: { version: 'detect' }
  },
  plugins: ['@typescript-eslint', 'react', 'react-hooks', 'functional', 'immutable'],
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react/recommended',
    'plugin:react-hooks/recommended'
  ],
  env: {
    browser: true,
    es2021: true
  },
  rules: {
    // Immutability
    'functional/immutable-data': ['error', { ignoreAccessorPattern: ['**.current', '**.mutable'] }],
    'immutable/no-mutation': 'error',
    'no-param-reassign': ['error', { props: true }],

    // React
    'react/react-in-jsx-scope': 'off',
    'react/prop-types': 'off',

    // TypeScript
    '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_', varsIgnorePattern: '^_' }]
  },
  overrides: [
    {
      files: ['**/*.ts', '**/*.tsx'],
      rules: {
        // Allow state refs etc.
        'functional/no-let': 'warn'
      }
    }
  ],
  ignorePatterns: ['dist/', 'node_modules/']
};

