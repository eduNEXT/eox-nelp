import React from 'react';
import ReactDOM from 'react-dom';


import {
  APP_INIT_ERROR, APP_READY, subscribe, initialize,
  mergeConfig,
  getConfig,
} from '@edx/frontend-platform';

import { ReportButton } from '@edunext/frontend-essentials'


function HelloWorld() {
  return <ReportButton />;
}

subscribe(APP_READY, () => {
  ReactDOM.render(<HelloWorld />, document.getElementById('root'));
});

initialize({  messages: []});
