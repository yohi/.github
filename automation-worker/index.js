import yaml from 'js-yaml';

export default {
  async fetch(request, env) {
    // POST以外のリクエストは拒否
    if (request.method !== 'POST') {
      return new Response('Method Not Allowed', { status: 405 });
    }

    try {
      const payload = await request.json();

      // リポジトリが新規作成（created）されたイベント以外は無視
      if (payload.action !== 'created' || !payload.repository) {
        return new Response('Event ignored', { status: 200 });
      }

      const newRepoName = payload.repository.name;
      const owner = payload.repository.owner.login;

      console.log(`Starting label sync for newly created repository: ${owner}/${newRepoName}`);

      // 1. .github リポジトリから labels.yml の中身（Rawデータ）を取得
      const configResponse = await fetch(
        `https://api.github.com/repos/${owner}/.github/contents/labels.yml`,
        {
          headers: {
            'Accept': 'application/vnd.github.v3.raw',
            'Authorization': `Bearer ${env.GH_PAT}`,
            'User-Agent': 'Cloudflare-Workers-GitHub-AutoLabeler',
            'X-GitHub-Api-Version': '2022-11-28'
          }
        }
      );

      if (!configResponse.ok) {
        throw new Error(`Failed to fetch labels.yml from .github repository. Status: ${configResponse.status}`);
      }

      const yamlText = await configResponse.text();
      
      // 2. labels.yml をパースしてラベルリストを取得
      const config = yaml.load(yamlText);
      const labels = config?.labels || [];

      console.log(`Loaded ${labels.length} labels from labels.yml`);

      // 3. 新規リポジトリに対して各ラベルを作成
      for (const label of labels) {
        if (!label.name) continue;

        console.log(`Creating label "${label.name}" in ${newRepoName}...`);

        const createResponse = await fetch(
          `https://api.github.com/repos/${owner}/${newRepoName}/labels`,
          {
            method: 'POST',
            headers: {
              'Accept': 'application/vnd.github.v3.raw',
              'Authorization': `Bearer ${env.GH_PAT}`,
              'User-Agent': 'Cloudflare-Workers-GitHub-AutoLabeler',
              'Content-Type': 'application/json',
              'X-GitHub-Api-Version': '2022-11-28'
            },
            body: JSON.stringify({
              name: label.name,
              color: label.color || 'cccccc',
              description: label.description || ''
            })
          }
        );

        if (createResponse.status === 422) {
          // すでに同名のラベルが存在する場合はスキップ
          console.log(`Label "${label.name}" already exists. Skipping.`);
        } else if (!createResponse.ok) {
          console.error(`Failed to create label "${label.name}". Status: ${createResponse.status}`);
        } else {
          console.log(`Successfully created label "${label.name}"`);
        }
      }

      return new Response('Label sync completed successfully', { status: 200 });

    } catch (error) {
      console.error('Error during label sync:', error.message);
      return new Response(`Internal Server Error: ${error.message}`, { status: 500 });
    }
  }
};
