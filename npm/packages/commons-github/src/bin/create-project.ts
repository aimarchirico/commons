#!/usr/bin/env node

import {resolveEnv} from '@aimarchirico/commons-ts/env';
import {fail, printSummary, report} from '@aimarchirico/commons-ts/report';
import {gh, ghJson, ghOrThrow, repoContext} from '../services/gh.js';

type Project = {number: number; title: string};

const nodes = (value: {nodes?: Project[]; Nodes?: Project[]}): Project[] =>
  value.nodes ?? value.Nodes ?? [];

const linkedProjects = (slug: string): Project[] => {
  const data = ghJson<{projectsV2: {nodes?: Project[]; Nodes?: Project[]}}>([
    'repo',
    'view',
    slug,
    '--json',
    'projectsV2',
  ]);
  return nodes(data.projectsV2);
};

const ownedProject = (owner: string, title: string): Project | undefined => {
  const result = gh(['project', 'list', '--owner', owner, '--format', 'json']);
  if (result.status !== 0) return undefined;
  const data = JSON.parse(result.stdout) as {projects?: Project[]};
  return (data.projects ?? []).find(project => project.title === title);
};

/**
 * Resolve the project linked to the repository this one was generated from.
 * Only readable while the template relationship is still reported, which is
 * why an override exists.
 */
const templateProject = (): {owner: string; number: number} | undefined => {
  const result = gh(['repo', 'view', '--json', 'templateRepository']);
  if (result.status !== 0) return undefined;
  const template = (
    JSON.parse(result.stdout) as {
      templateRepository?: {owner?: {login: string}; name?: string};
    }
  ).templateRepository;
  const owner = template?.owner?.login;
  const name = template?.name;
  if (!owner || !name) return undefined;

  const source = gh([
    'repo',
    'view',
    `${owner}/${name}`,
    '--json',
    'projectsV2',
  ]);
  if (source.status !== 0) return undefined;
  const found = nodes(
    (JSON.parse(source.stdout) as {projectsV2: {nodes?: Project[]}}).projectsV2,
  )[0];
  return found ? {owner, number: found.number} : undefined;
};

const link = (owner: string, slug: string, number: number): void => {
  ghOrThrow(['project', 'link', String(number), '--owner', owner, '-R', slug]);
};

const env = resolveEnv(
  ['PROJECT_TITLE'],
  ['PROJECT_SOURCE_OWNER', 'PROJECT_SOURCE_NUMBER'],
);
const title = env.PROJECT_TITLE;
const {owner, slug} = repoContext();

try {
  const linked = linkedProjects(slug).find(project => project.title === title);
  if (linked) {
    report(
      `project "${title}"`,
      'present',
      `#${linked.number} linked to ${slug}`,
    );
  } else {
    const existing = ownedProject(owner, title);
    if (existing) {
      link(owner, slug, existing.number);
      report(`project "${title}"`, 'updated', `#${existing.number} linked`);
    } else {
      const override =
        env.PROJECT_SOURCE_OWNER && env.PROJECT_SOURCE_NUMBER
          ? {
              owner: env.PROJECT_SOURCE_OWNER,
              number: Number(env.PROJECT_SOURCE_NUMBER),
            }
          : undefined;
      const source = override ?? templateProject();
      if (!source) {
        fail(
          'Could not resolve a source project to copy. Set PROJECT_SOURCE_OWNER and PROJECT_SOURCE_NUMBER, or run this while the repository still reports the template it was generated from.',
        );
      }
      const copied = JSON.parse(
        ghOrThrow([
          'project',
          'copy',
          String(source.number),
          '--source-owner',
          source.owner,
          '--target-owner',
          owner,
          '--title',
          title,
          '--format',
          'json',
        ]),
      ) as {number: number};
      link(owner, slug, copied.number);
      report(
        `project "${title}"`,
        'created',
        `#${copied.number} copied from ${source.owner}/#${source.number}`,
      );
    }
  }
} catch (error) {
  fail(error instanceof Error ? error.message : String(error));
}

printSummary('create-project');
