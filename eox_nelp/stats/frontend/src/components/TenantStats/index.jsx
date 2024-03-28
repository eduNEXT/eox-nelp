import React, { useState} from 'react';
import ReactDOM from 'react-dom';
import { APP_INIT_ERROR, APP_READY, subscribe, initialize } from '@edx/frontend-platform';
import { StatsContainer, messages as essentialsMessages } from '@edunext/frontend-essentials'
import { AppProvider } from '@edx/frontend-platform/react';

import './index.scss';

function LaunchStatsContainer() {
  return (
    <AppProvider>
      <StatsContainer
        showVideos={showVideos}
        showCourses={showCourses}
        showProblems={showProblems}
        showLearners={showLearners}
        showInstructors={showInstructors}
        showCertificates={showCertificates}
      />
    </AppProvider>
  );
}

subscribe(APP_READY, () => {
  ReactDOM.render(<LaunchStatsContainer />, document.getElementById('tenant-stats'));
});

initialize({  messages: [essentialsMessages]});
