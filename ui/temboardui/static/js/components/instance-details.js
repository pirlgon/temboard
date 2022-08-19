/* eslint-env es6 */
/* global instances, Vue, VueRouter, Dygraph, moment, _, getParameterByName */
$(function() { Vue.component('instance-details', {
  /* An instance identity card */
  props: [
    'pg_host',
    'pg_port',
    'pg_data',
    'pg_version_summary',
    'cpu',
    'mem_gb',
  ],
  template: `
  <div class="alert alert-light mx-auto pa-6">
    <h2 class="text-center"><span v-html="pg_host"/>:<span v-html="pg_port"/></h2>
    <p class="text-center">
      <span v-if="cpu && mem_gb"><span v-html="cpu"/> CPU - <span v-html="mem_gb"/> GB memory<br/></span>
      <strong v-if="pg_version_summary && pg_data"><span v-html="pg_version_summary"/> serving <span v-html="pg_data"/>.</strong><br/>
    </p>
  </div>
  `
})});
