import React from 'react';
import ReactDOM from 'react-dom';
import { APP_INIT_ERROR, APP_READY, subscribe, initialize } from '@edx/frontend-platform';
import { PhoneValidatorModal, messages as essentialsMessages } from '@edunext/frontend-essentials';
import { AppProvider } from '@edx/frontend-platform/react';

import './index.scss';

function LaunchPhoneValidator() {

  return (
    <AppProvider>
      <PhoneValidatorModal />
    </AppProvider>
  );
}

subscribe(APP_READY, () => {
  ReactDOM.render(<LaunchPhoneValidator />, document.getElementById('phone-validation'));
});

initialize({ messages: [essentialsMessages] });
