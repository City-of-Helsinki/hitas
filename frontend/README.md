# Hitas frontend

This is the frontend for Hitas management, for the City of Helsinki.\
It was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## To start

The project uses yarn for package management.\
First install Yarn (if not already installed):

#### `npm install -g yarn`

Install necessary node-packages:

##### `yarn install`

Then run the app (in the development mode):

#### `yarn start`

Your browser should open a new window/tab with the app automatically.\
It runs in [http://localhost:3000](http://localhost:3000) in your browser

The page will reload if you make edits.\
You will also see any lint errors in the console.

### Other available Scripts

In the project directory, you can also run:

#### `yarn test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

#### `yarn build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

#### `yarn eslint-check`

Checks for possibly conflicting rules between eslint and prettier

#### `yarn run prettier-format`

Checks (and when possible, fixes) prettier linting of the relevant files in the entire project

### Miscellaneous

This project makes use of components from `hds-react` and `hds-core/hds-design-tokens` style abstractions.\
(from the [Helsinki Design System](https://hds.hel.fi))
