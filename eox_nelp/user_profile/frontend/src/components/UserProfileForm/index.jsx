import React from 'react';
import ReactDOM from 'react-dom';
import { APP_INIT_ERROR, APP_READY, subscribe, initialize } from '@edx/frontend-platform';
import { ProfileDataModal } from '@edunext/frontend-essentials';
import { AppProvider } from '@edx/frontend-platform/react';

import messages from '../../../../../i18n';
import './index.scss';

function LaunchUserProfileForm() {

  return (
    <AppProvider>
      <ProfileDataModal />
    </AppProvider>
  );
}

subscribe(APP_READY, () => {
  ReactDOM.render(<LaunchUserProfileForm />, document.getElementById('user-profile-data-form'));
});

initialize({ messages });
