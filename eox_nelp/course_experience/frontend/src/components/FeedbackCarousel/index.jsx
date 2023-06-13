import React from 'react';
import ReactDOM from 'react-dom';


import {
  APP_INIT_ERROR, APP_READY, subscribe, initialize,
  mergeConfig,
  getConfig,
} from '@edx/frontend-platform';

import { ReportButton, FeedbackCarousel } from '@edunext/frontend-essentials'


function HelloWorld() {
  return <ReportButton />;
}

function LaunchFeedbackCarousel() {
  return <FeedbackCarousel />;
}

subscribe(APP_READY, () => {
  ReactDOM.render(<HelloWorld />, document.getElementById('root'));
  ReactDOM.render(<LaunchFeedbackCarousel />, document.getElementById('carousel'));

});

initialize({  messages: []});
