import React, { useState} from 'react';
import ReactDOM from 'react-dom';
import { APP_INIT_ERROR, APP_READY, subscribe, initialize } from '@edx/frontend-platform';
import { PhoneValidatorModal, messages as essentialsMessages } from '@edunext/frontend-essentials';
import { AppProvider } from '@edx/frontend-platform/react';

import './index.scss';

function LaunchStatsContainer() {
  const [locale, setLocale] = useState(getLocale());

  return (
    <AppProvider>
      <PhoneValidatorModal />
    </AppProvider>
  );
}

subscribe(APP_READY, () => {
  ReactDOM.render(<LaunchPhoneValidator />, document.getElementById('tenant-stats'));
});

initialize({  messages: [essentialsMessages]});
