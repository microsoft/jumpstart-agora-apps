const windowConfig: any = window;

//handles getting variables from either the window or the process
export const getEnvVariable = (key: string): string | undefined => {
    var value = undefined;

    if (windowConfig._env_ && windowConfig._env_[key]) {
        value = windowConfig._env_[key];
    } else if (process.env[key]) {
        value = process.env[key] ?? "";
    } else {
        console.error(`Env variable ${key} not found`);
    }
    return value;
};
