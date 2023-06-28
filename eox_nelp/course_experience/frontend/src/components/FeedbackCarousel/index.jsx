import React, { useState} from 'react';
import ReactDOM from 'react-dom';
import { APP_INIT_ERROR, APP_READY, subscribe, initialize } from '@edx/frontend-platform';
import { getLocale, getMessages, IntlProvider } from '@edx/frontend-platform/i18n';
import { FeedbackCarousel, messages as essentialsMessages } from '@edunext/frontend-essentials'

import './index.scss';


function LaunchFeedbackCarousel() {
  const [locale, setLocale] = useState(getLocale());

  return (
    <IntlProvider locale={locale} messages={getMessages()}>
      <FeedbackCarousel />
    </IntlProvider>
  );
}

subscribe(APP_READY, () => {
  ReactDOM.render(<LaunchFeedbackCarousel />, document.getElementById('feedback-courses-carousel'));

});

initialize({  messages: [essentialsMessages]});
