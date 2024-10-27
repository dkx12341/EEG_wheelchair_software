using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class ColorControler : MonoBehaviour
{
    // Start is called before the first frame update
    public Material[] colourMaterials;
    public TMPro.TMP_Dropdown dropdown;
    public Image image;

    //Material currentlySelectedMaterial;
    public Dictionary<string, Material> coloursDic = new Dictionary<string, Material>();
    void Start()
    {
        image = GetComponent<Image>();
        colourMaterials = Resources.LoadAll<Material>("Materials/");
        List<string> names = new List<string>();

        foreach (Material mat in colourMaterials)
        {
            names.Add(mat.name);
            coloursDic.Add(mat.name, mat);
        }

        dropdown.AddOptions(names);
    }

    public void OnValueChange()
    {
        image.color = coloursDic[dropdown.captionText.text].color;
    }

    // Update is called once per frame

}
