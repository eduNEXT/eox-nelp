import React, { useState} from 'react';
import ReactDOM from 'react-dom';
import { APP_INIT_ERROR, APP_READY, subscribe, initialize } from '@edx/frontend-platform';
import { getLocale, getMessages, IntlProvider } from '@edx/frontend-platform/i18n';
import { StatsContainer, messages as essentialsMessages } from '@edunext/frontend-essentials'

import './index.scss';

function LaunchStatsContainer() {
  const [locale, setLocale] = useState(getLocale());

  return (
    <IntlProvider locale={locale} messages={getMessages()}>
      <StatsContainer
        showVideos={showVideos}
        showCourses={showCourses}
        showProblems={showProblems}
        showLearners={showLearners}
        showInstructors={showInstructors}
        showCertificates={showCertificates}
      />
    </IntlProvider>
  );
}

subscribe(APP_READY, () => {
  ReactDOM.render(<LaunchStatsContainer />, document.getElementById('tenant-stats'));
});

initialize({  messages: [essentialsMessages]});
