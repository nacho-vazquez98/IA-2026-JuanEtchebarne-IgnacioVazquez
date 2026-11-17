"""Validación breve y reproducible del ejemplo de Acrobot, sin renderizar."""

import gymnasium as gym
import numpy as np

SEMILLA = 42
MAX_PASOS = 700


def ejecutar_episodio(impulso=False):
    env = gym.make("Acrobot-v1", render_mode=None, max_episode_steps=MAX_PASOS)
    try:
        assert env.observation_space.shape == (6,)
        assert env.observation_space.dtype == np.float32
        assert env.action_space == gym.spaces.Discrete(3)

        obs, _ = env.reset(seed=SEMILLA)
        env.action_space.seed(SEMILLA)
        assert env.observation_space.contains(obs)
        observaciones = [obs]
        transiciones = []
        for paso in range(1, MAX_PASOS + 1):
            # Para cubrir el éxito, aplicar torque en el sentido de la segunda velocidad.
            if impulso:
                accion = 2 if obs[5] >= 0 else 0
            else:
                accion = env.action_space.sample()
            assert env.action_space.contains(accion)
            obs, recompensa, terminado, truncado, _ = env.step(accion)
            assert env.observation_space.contains(obs)
            assert recompensa == (0.0 if terminado else -1.0)
            assert not truncado or paso == MAX_PASOS
            observaciones.append(obs)
            transiciones.append((int(accion), recompensa, terminado, truncado))
            if terminado or truncado:
                break
        assert terminado or truncado
        return np.stack(observaciones), transiciones
    finally:
        env.close()


def verificar_repeticion(impulso):
    observaciones, transiciones = ejecutar_episodio(impulso)
    repeticion, transiciones_repetidas = ejecutar_episodio(impulso)
    np.testing.assert_array_equal(observaciones, repeticion)
    assert transiciones == transiciones_repetidas
    acciones, recompensas, _, _ = zip(*transiciones)
    _, _, terminado, truncado = transiciones[-1]
    assert (terminado, truncado) == (impulso, not impulso)
    politica = "impulso" if impulso else "aleatoria"
    print(f"Política: {politica}")
    print(f"Pasos: {len(transiciones)}, retorno: {sum(recompensas):g}")
    print(f"Acciones: {sorted(set(acciones))}, recompensas: {sorted(set(recompensas))}")
    print(f"Terminado: {terminado}, truncado: {truncado}")
    print(f"Mínimos observados: {observaciones.min(axis=0).round(4)}")
    print(f"Máximos observados: {observaciones.max(axis=0).round(4)}")
    print("Repetición idéntica.")


if __name__ == "__main__":
    print(f"Gymnasium {gym.__version__}, NumPy {np.__version__}, semilla {SEMILLA}")
    verificar_repeticion(impulso=False)
    verificar_repeticion(impulso=True)
