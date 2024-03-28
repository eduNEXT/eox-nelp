import React, { useState} from 'react';
import ReactDOM from 'react-dom';
import { APP_INIT_ERROR, APP_READY, subscribe, initialize } from '@edx/frontend-platform';
import { FeedbackCarousel, messages as essentialsMessages } from '@edunext/frontend-essentials'
import { AppProvider } from '@edx/frontend-platform/react';

import './index.scss';


function LaunchFeedbackCarousel() {
  return (
    <AppProvider>
      <FeedbackCarousel />
    </AppProvider>
  );
}

subscribe(APP_READY, () => {
  ReactDOM.render(<LaunchFeedbackCarousel />, document.getElementById('feedback-courses-carousel'));

});

initialize({  messages: [essentialsMessages]});
