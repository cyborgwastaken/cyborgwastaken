module.exports = {
  apps: [
    {
      name: "portfolio",
      script: "npm",
      args: " run dev",
      cwd: __dirname,
      env: {
        NODE_ENV: "production",
        PORT: 3000,
      },
    },
  ],
};
