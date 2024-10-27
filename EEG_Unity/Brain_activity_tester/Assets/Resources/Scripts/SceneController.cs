using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

public class SceneController : MonoBehaviour
{
    int currentSceneNumber;
    // Start is called before the first frame update
    void Start()
    {
        currentSceneNumber = SceneManager.GetActiveScene().buildIndex;
    }

    // Update is called once per frame
   public void OnNextClick()
    {
        SceneManager.LoadScene(currentSceneNumber + 1);
    }

    public void OnPreviousClick()
    {
        SceneManager.LoadScene(currentSceneNumber - 1);
    }
    public void OnFinishClick()
    {
        Application.Quit();
    }
}
